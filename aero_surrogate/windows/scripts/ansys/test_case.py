"""
PyMechanical Template-Based Workflow - Working Version
Solves 3 test cases using template (same geometry for now)
"""

import os
import pandas as pd
from pathlib import Path

os.environ["ANSYS_MECHANICAL_NO_SECURITY"] = "1"

print("Importing PyMechanical...")
from ansys.mechanical.core import App

# ============================================================================
# CONFIGURATION
# ============================================================================
STEP_FOLDER = (
    r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\datasets\FEA\cases"
)
TEMPLATE_MECHDAT = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\workbench\template_project\blade_body_template.mechdat"
OUTPUT_CSV = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\fea_results\fea_results.csv"

YIELD_STRENGTH = 1.1e9  # Pa

NUM_TEST_CASES = 3

print("\nConfiguration:")
print(f"  Template:    {TEMPLATE_MECHDAT}")
print(f"  Output CSV:  {OUTPUT_CSV}")
print(f"  Test cases:  {NUM_TEST_CASES}\n")

# Validate
if not Path(TEMPLATE_MECHDAT).exists():
    print(f"❌ Template not found: {TEMPLATE_MECHDAT}")
    exit(1)

step_files = sorted(Path(STEP_FOLDER).glob("*.step"))[:NUM_TEST_CASES]
if len(step_files) == 0:
    print(f"❌ No STEP files found")
    exit(1)

Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

print(f"✓ Found {len(step_files)} STEP files")
print(f"✓ Template validated\n")

# ============================================================================
# LAUNCH MECHANICAL ONCE
# ============================================================================
print("=" * 80)
print("LAUNCHING MECHANICAL")
print("=" * 80)
print("This takes 1-2 minutes...\n")

mechanical = App()
print(f"✅ Mechanical launched (version {mechanical.version})\n")

# ============================================================================
# PROCESS CASES
# ============================================================================
print("=" * 80)
print("PROCESSING CASES")
print("=" * 80)
print("NOTE: Using template geometry for all cases (geometry swap not available)\n")

results = []

for idx, step_file in enumerate(step_files, 1):
    print(f"CASE {idx}/{len(step_files)}: {step_file.stem}")
    print("-" * 80)

    try:
        # Open template
        print("  [1/5] Opening template...")
        mechanical.open(TEMPLATE_MECHDAT)
        print("  ✓ Template opened")

        # Access model
        print("  [2/5] Accessing model...")
        model = mechanical.DataModel.Project.Model
        geometry = model.Geometry
        analysis = model.Analyses[0]

        print(f"  ✓ Model ready (geometry parts: {len(geometry.Children)})")

        # Generate mesh
        print("  [3/5] Generating mesh...")
        mesh = model.Mesh
        mesh.GenerateMesh()
        print(f"  ✓ Mesh: {mesh.Nodes} nodes, {mesh.Elements} elements")

        # Solve
        print("  [4/5] Solving...")
        solution = analysis.Solution
        solution.Solve(True)
        print("  ✓ Solution complete")

        # Extract results
        print("  [5/5] Extracting results...")

        # Find stress result
        stress_result = None
        for child in solution.Children:
            child_type = str(type(child))
            if "Stress" in child_type and hasattr(child, "Maximum"):
                stress_result = child
                break

        if not stress_result:
            raise Exception("No stress result found in solution")

        # Get values
        max_stress = float(stress_result.Maximum.Value)
        volume = float(geometry.Volume.Value)
        mass = float(geometry.Mass.Value)

        # Calculate margin of safety
        if max_stress > 0:
            design_load = 1.1 * max_stress
            mos = (YIELD_STRENGTH / design_load) - 1.0
        else:
            mos = 999.0

        # Store results
        results.append(
            {
                "case_label": step_file.stem,
                "step_file": str(step_file),
                "max_stress_Pa": max_stress,
                "volume_m3": volume,
                "mass_kg": mass,
                "yield_strength_Pa": YIELD_STRENGTH,
                "margin_of_safety": mos,
                "status": "SUCCESS",
            }
        )

        print(f"  ✅ SUCCESS")
        print(f"     Max Stress: {max_stress:.2e} Pa")
        print(f"     Volume:     {volume:.6e} m³")
        print(f"     Mass:       {mass:.6e} kg")
        print(f"     MoS:        {mos:.3f}")

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback

        traceback.print_exc()

        results.append(
            {
                "case_label": step_file.stem,
                "step_file": str(step_file),
                "max_stress_Pa": None,
                "volume_m3": None,
                "mass_kg": None,
                "yield_strength_Pa": YIELD_STRENGTH,
                "margin_of_safety": None,
                "status": f"FAILED: {str(e)}",
            }
        )

    print()

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("=" * 80)
print("SAVING RESULTS")
print("=" * 80)

df = pd.DataFrame(results)
df.to_csv(OUTPUT_CSV, index=False)

print(f"✓ Results saved to:\n  {OUTPUT_CSV}\n")

# Summary
successful = len([r for r in results if r["status"] == "SUCCESS"])
failed = len(results) - successful

print("SUMMARY:")
print(f"  ✅ Successful: {successful}/{len(results)}")
print(f"  ❌ Failed:     {failed}/{len(results)}")

if successful > 0:
    print("\nResults preview:")
    success_df = df[df["status"] == "SUCCESS"]
    print(
        success_df[["case_label", "max_stress_Pa", "margin_of_safety"]].to_string(
            index=False
        )
    )

# ============================================================================
# CLEANUP
# ============================================================================
print("\n" + "=" * 80)
print("CLOSING MECHANICAL")
print("=" * 80)
mechanical.exit()
print("✓ Done!\n")

print("=" * 80)
print("IMPORTANT NOTE")
print("=" * 80)
print("⚠️  All 3 cases used the SAME geometry from the template.")
print("   Results will be identical because geometry didn't change.")
print("\nTo get different results for each case, you need:")
print("  1. ANSYS SP03+ update (enables gRPC mode)")
print("  2. OR manually create 300 .mechdat files with different geometry")
print("  3. OR use Workbench journaling (fragile but possible)")
print("=" * 80)
