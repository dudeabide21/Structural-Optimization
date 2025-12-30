import os
import re
import glob
import argparse
import numpy as np

from OCC.Core.gp import gp_Pnt
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepCheck import BRepCheck_Analyzer
from OCC.Core.BRepGProp import brepgprop_VolumeProperties
from OCC.Core.GProp import GProp_GProps
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone


SEC_RE = re.compile(r"^sec(\d+)\.", re.IGNORECASE)


def load_section_points(path: str):
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[None, :]
    if data.shape[1] < 3:
        raise ValueError(f"{path} does not have at least 3 columns")
    return data[:, 0], data[:, 1], data[:, 2]


def bspline_wire_from_xyz(x, y, z, tol=1e-6):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    z = np.asarray(z, dtype=float)

    # Ensure closed loop
    dx, dy, dz = x[-1] - x[0], y[-1] - y[0], z[-1] - z[0]
    if dx * dx + dy * dy + dz * dz > tol**2:
        x = np.append(x, x[0])
        y = np.append(y, y[0])
        z = np.append(z, z[0])

    n = len(x)
    pts = TColgp_Array1OfPnt(1, n)
    for i in range(n):
        pts.SetValue(i + 1, gp_Pnt(float(x[i]), float(y[i]), float(z[i])))

    curve = GeomAPI_PointsToBSpline(pts).Curve()
    edge = BRepBuilderAPI_MakeEdge(curve).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return wire


def get_sorted_section_paths(case_dir: str):
    # Only match sec*.dat and sort by the number right after "sec"
    paths = glob.glob(os.path.join(case_dir, "sec*.dat"))
    numbered = []
    for p in paths:
        base = os.path.basename(p)
        m = SEC_RE.match(base)
        if not m:
            continue
        numbered.append((int(m.group(1)), p))
    numbered.sort(key=lambda t: t[0])
    return [p for _, p in numbered]


def build_blade_solid_from_case(case_dir: str, expected_sections: int = 21):
    sec_paths = get_sorted_section_paths(case_dir)
    if not sec_paths:
        raise FileNotFoundError(f"No sec*.dat files found in {case_dir}")

    if expected_sections is not None and len(sec_paths) != expected_sections:
        raise RuntimeError(
            f"Expected {expected_sections} sections but found {len(sec_paths)} in {case_dir}"
        )

    loft = BRepOffsetAPI_ThruSections(True, False)
    loft.CheckCompatibility(True)

    for sec_path in sec_paths:
        x, y, z = load_section_points(sec_path)
        wire = bspline_wire_from_xyz(x, y, z)
        loft.AddWire(wire)

    loft.Build()
    if not loft.IsDone():
        raise RuntimeError("Loft failed")

    shape = loft.Shape()

    analyzer = BRepCheck_Analyzer(shape)
    if not analyzer.IsValid():
        # Not always fatal, but warn
        print(f"[WARN] OCC reports invalid shape: {case_dir}")

    pprops = GProp_GProps()
    brepgprop_VolumeProperties(shape, pprops)
    vol = pprops.Mass()  # volume in model units^3
    return shape, vol


def export_step(shape, out_path: str):
    writer = STEPControl_Writer()
    if writer.Transfer(shape, STEPControl_AsIs) != IFSelect_RetDone:
        raise RuntimeError("STEP transfer failed")
    if writer.Write(out_path) != IFSelect_RetDone:
        raise RuntimeError(f"Failed to write STEP: {out_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cases-root", required=True, help="Path containing case_0001 ... case_0300"
    )
    ap.add_argument("--pattern", default="case_*", help="Glob pattern under cases-root")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--expected-sections", type=int, default=21)
    ap.add_argument("--out-name", default="blade_{case}.step")
    ap.add_argument("--log", default=None, help="Optional log file path")
    args = ap.parse_args()

    case_dirs = sorted(glob.glob(os.path.join(args.cases_root, args.pattern)))
    if not case_dirs:
        raise SystemExit(
            f"No case directories found under {args.cases_root} with {args.pattern}"
        )

    log_f = open(args.log, "w") if args.log else None

    def log(msg: str):
        print(msg)
        if log_f:
            log_f.write(msg + "\n")
            log_f.flush()

    ok = 0
    fail = 0

    for case_dir in case_dirs:
        case = os.path.basename(case_dir)
        out_path = os.path.join(case_dir, args.out_name.format(case=case))

        if (not args.overwrite) and os.path.isfile(out_path):
            log(f"[SKIP] {case}: STEP exists")
            continue

        try:
            shape, vol = build_blade_solid_from_case(
                case_dir, expected_sections=args.expected_sections
            )
            if vol <= 0:
                raise RuntimeError(f"Volume <= 0 (got {vol})")

            export_step(shape, out_path)
            log(f"[OK] {case}: wrote {out_path} | OCC volume={vol}")
            ok += 1
        except Exception as e:
            log(f"[FAIL] {case}: {e}")
            fail += 1

    if log_f:
        log_f.close()

    print(f"\nDONE. ok={ok}, fail={fail}")
    if fail:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
