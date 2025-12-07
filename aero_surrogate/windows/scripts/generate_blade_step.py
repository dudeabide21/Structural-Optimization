import os
import glob
import numpy as np

from OCC.Core.gp import gp_Pnt
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone


def load_section_points(path):
    """Load XYZ points from a sec*.dat file."""
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[None, :]
    if data.shape[1] < 3:
        raise ValueError(f"{path} does not have at least 3 columns")
    # take first three columns as X, Y, Z
    return data[:, 0], data[:, 1], data[:, 2]


def bspline_wire_from_xyz(x, y, z):
    """Create a closed B-spline wire from XYZ arrays."""
    n = len(x)
    pts = TColgp_Array1OfPnt(1, n)
    for i in range(n):
        pts.SetValue(i + 1, gp_Pnt(float(x[i]), float(y[i]), float(z[i])))

    bspline_curve = GeomAPI_PointsToBSpline(pts).Curve()
    edge = BRepBuilderAPI_MakeEdge(bspline_curve).Edge()
    wire = BRepBuilderAPI_MakeWire(edge).Wire()
    return wire


def build_blade_solid_from_case(case_dir, case_label="case"):
    """Build a lofted blade solid from all sec*.dat files in case_dir."""
    pattern = os.path.join(case_dir, "sec*.dat")
    sec_paths = sorted(
        glob.glob(pattern),
        key=lambda p: int(
            "".join(ch for ch in os.path.basename(p) if ch.isdigit()) or "0"
        ),
    )

    if not sec_paths:
        raise FileNotFoundError(f"No sec*.dat files found in {case_dir}")

    print(f"Found {len(sec_paths)} sections for {case_label}:")
    for p in sec_paths:
        print("  ", os.path.basename(p))

    loft = BRepOffsetAPI_ThruSections(True, False, 1.0)  # solid, not ruled
    for sec_path in sec_paths:
        x, y, z = load_section_points(sec_path)
        wire = bspline_wire_from_xyz(x, y, z)
        loft.AddWire(wire)

    loft.Build()
    if not loft.IsDone():
        raise RuntimeError("Loft failed.")
    return loft.Shape()


def export_step(shape, out_path):
    """Export a TopoDS_Shape to a STEP file."""
    writer = STEPControl_Writer()
    status = writer.Transfer(shape, STEPControl_AsIs)
    if status != IFSelect_RetDone:
        raise RuntimeError("STEP transfer failed.")
    status = writer.Write(out_path)
    if status != IFSelect_RetDone:
        raise RuntimeError(f"Failed to write STEP file: {out_path}")
    print(f"Exported STEP: {out_path}")


if __name__ == "__main__":
    CASE_DIR = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\wsl\fea_cases\case_0001"
    CASE_LABEL = "case_0001"

    shape = build_blade_solid_from_case(CASE_DIR, CASE_LABEL)
    out_step = os.path.join(CASE_DIR, f"blade_{CASE_LABEL}.step")
    export_step(shape, out_step)
