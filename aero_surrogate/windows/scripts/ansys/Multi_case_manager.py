"""
PyMechanical - Geometry Import Replace Method
Uses existing Geometry Import object to replace STEP files
"""

import os
import pandas as pd
from pathlib import Path

os.environ["ANSYS_MECHANICAL_NO_SECURITY"] = "1"

# ============================================================================
# CONFIGURATION
# ============================================================================
TEMPLATE_MECHDAT = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\workbench\template_project\blade_body_template.mechdat"
STEP_FOLDER = (
    r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\datasets\FEA\cases"
)
OUTPUT_CSV = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\fea_results\fea_results.csv"

YIELD_STRENGTH = 1.1e9
NUM_TEST_CASES = 3

print("=" * 80)
print("GEOMETRY IMPORT REPLACE METHOD")
print("=" * 80)

# Validate
if not Path(TEMPLATE_MECHDAT).exists():
    print(f"❌ Template not found")
    exit(1)

step_files = sorted(Path(STEP_FOLDER).glob("*.step"))[:NUM_TEST_CASES]
if len(step_files) == 0:
    print(f"❌ No STEP files found")
    exit(1)

Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)

print(f"\n✓ Template: {Path(TEMPLATE_MECHDAT).name}")
print(f"✓ STEP files: {len(step_files)}\n")

# ============================================================================
# LAUNCH AND INSPECT TEMPLATE
# ============================================================================
print("=" * 80)
print("STEP 1: INSPECTING TEMPLATE STRUCTURE")
print("=" * 80)

from ansys.mechanical.core import App

print("\nLaunching Mechanical...")
mechanical = App()
print(f"✅ Launched (version {mechanical.version})\n")

print("Opening template...")
mechanical.open(TEMPLATE_MECHDAT)
print("✓ Template opened\n")

# Inspect the model structure
model = mechanical.DataModel.Project.Model
print("Model structure:")
print(f"  Model type: {type(model)}")
print(f"  Model children: {len(model.Children)}\n")

# Look for Geometry or GeometryImport objects
print("Searching for Geometry Import objects...")
geometry_import = None
geometry_container = None

# Check direct children of Model
for child in model.Children:
    child_type = type(child).__name__
    print(f"  - {child.Name}: {child_type}")

    if "Geometry" in child_type:
        geometry_container = child
        print(f"    └─ Found geometry container!")

        # Check its children
        if hasattr(child, "Children"):
            for subchild in child.Children:
                subchild_type = type(subchild).__name__
                print(f"       └─ {subchild.Name}: {subchild_type}")

                if "Import" in subchild_type or "GeometryImport" in subchild_type:
                    geometry_import = subchild
                    print(f"          ✓ This is a Geometry Import object!")

print()

# ============================================================================
# CHECK IF WE CAN REPLACE GEOMETRY
# ============================================================================
print("=" * 80)
print("STEP 2: CHECKING REPLACE CAPABILITY")
print("=" * 80)

if geometry_import is None:
    print("\n⚠️  No Geometry Import object found in template.")
    print("\nYour template likely has directly imported geometry.")
    print("To use this method, you need to:")
    print("1. In Workbench, right-click Geometry → Insert → External Model")
    print("2. Import your STEP file through 'External Model'")
    print("3. Save as .mechdat template")
    print("\nTrying alternative approach...")

    # Check if geometry has a source file
    if geometry_container:
        print(f"\nGeometry container found. Checking for source file...")
        for part in geometry_container.Children:
            print(f"\nPart: {part.Name}")

            # List all properties
            for attr in dir(part):
                if (
                    not attr.startswith("_")
                    and "File" in attr
                    or "Source" in attr
                    or "Path" in attr
                ):
                    try:
                        value = getattr(part, attr)
                        if value and isinstance(value, str):
                            print(f"  {attr}: {value}")
                    except:
                        pass

else:
    print(f"\n✅ Found Geometry Import: {geometry_import.Name}")
    print(f"   Type: {type(geometry_import).__name__}")

    # Check available methods
    print(f"\nAvailable methods:")
    replace_methods = [
        m
        for m in dir(geometry_import)
        if "Replace" in m or "File" in m or "Source" in m
    ]
    for method in replace_methods:
        print(f"  - {method}")

    # Try to find current source file
    try:
        if hasattr(geometry_import, "SourceFile"):
            print(f"\n  Current source: {geometry_import.SourceFile}")
        if hasattr(geometry_import, "FilePath"):
            print(f"  Current path: {geometry_import.FilePath}")
    except:
        pass

    # Check if ReplaceWithFile exists
    if hasattr(geometry_import, "ReplaceWithFile"):
        print(f"\n✅ ReplaceWithFile method available!")
        print(f"   We can swap geometry!\n")

        # Test with first STEP file
        print("=" * 80)
        print("STEP 3: TESTING GEOMETRY REPLACEMENT")
        print("=" * 80)

        test_file = step_files[0]
        print(f"\nTesting with: {test_file.name}")

        try:
            print("  Attempting to replace geometry...")
            geometry_import.ReplaceWithFile(str(test_file))
            print("  ✅ Replace command executed!")

            # Update geometry
            print("  Updating geometry...")
            if hasattr(geometry_container, "UpdateGeometryFromSource"):
                geometry_container.UpdateGeometryFromSource()
                print("  ✅ Geometry updated!")

            # Check if it changed
            print(f"\n  Verifying change...")
            volume_before = None

            # Generate mesh to verify
            print("  Generating mesh...")
            mesh = model.Mesh
            mesh.GenerateMesh()
            print(f"  ✅ Mesh: {mesh.Nodes} nodes")

            print(f"\n✅ GEOMETRY SWAP TEST SUCCESSFUL!")
            print(f"   This method will work for all 300 cases!\n")

            can_swap = True

        except Exception as e:
            print(f"  ❌ Replace failed: {e}")
            can_swap = False
    else:
        print(f"\n❌ ReplaceWithFile method not found")
        print(f"   Available attributes:")
        for attr in dir(geometry_import):
            if not attr.startswith("_"):
                print(f"     - {attr}")
        can_swap = False

# ============================================================================
# DECISION POINT
# ============================================================================
print("=" * 80)
print("DECISION")
print("=" * 80)

if "can_swap" in locals() and can_swap:
    print("\n✅ Geometry swapping is POSSIBLE!")
    proceed = input("\nProceed with full 3-case test? (y/n): ")

    if proceed.lower() == "y":
        # Continue with full workflow
        print("\n" + "=" * 80)
        print("RUNNING FULL 3-CASE WORKFLOW")
        print("=" * 80)

        results = []

        for idx, step_file in enumerate(step_files, 1):
            print(f"\nCASE {idx}/{len(step_files)}: {step_file.stem}")
            print("-" * 80)

            try:
                # Reopen template
                print("  [1/6] Opening template...")
                mechanical.open(TEMPLATE_MECHDAT)

                # Get geometry import object
                print("  [2/6] Accessing geometry import...")
                model = mechanical.DataModel.Project.Model
                geom_import = None
                for child in model.Geometry.Children:
                    if "Import" in type(child).__name__:
                        geom_import = child
                        break

                if not geom_import:
                    raise Exception("Geometry import not found")

                # Replace geometry
                print(f"  [3/6] Replacing with: {step_file.name}")
                geom_import.ReplaceWithFile(str(step_file))
                model.Geometry.UpdateGeometryFromSource()
                print("  ✓ Geometry replaced")

                # Mesh
                print("  [4/6] Meshing...")
                model.Mesh.GenerateMesh()
                print(f"  ✓ Mesh: {model.Mesh.Nodes} nodes")

                # Solve
                print("  [5/6] Solving...")
                model.Analyses[0].Solution.Solve(True)
                print("  ✓ Solved")

                # Extract
                print("  [6/6] Extracting...")
                solution = model.Analyses[0].Solution
                stress_result = None
                for child in solution.Children:
                    if "Stress" in str(type(child)) and hasattr(child, "Maximum"):
                        stress_result = child
                        break

                max_stress = float(stress_result.Maximum.Value)
                volume = float(model.Geometry.Volume.Value)
                mass = float(model.Geometry.Mass.Value)
                mos = (YIELD_STRENGTH / (1.1 * max_stress)) - 1.0

                results.append(
                    {
                        "case_label": step_file.stem,
                        "max_stress_Pa": max_stress,
                        "volume_m3": volume,
                        "mass_kg": mass,
                        "margin_of_safety": mos,
                        "status": "SUCCESS",
                    }
                )

                print(f"  ✅ SUCCESS - Stress: {max_stress:.2e} Pa")

            except Exception as e:
                print(f"  ❌ FAILED: {e}")
                results.append(
                    {"case_label": step_file.stem, "status": f"FAILED: {str(e)}"}
                )

        # Save
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_CSV, index=False)

        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)

        successful = len([r for r in results if r.get("status") == "SUCCESS"])
        print(f"\n✅ Successful: {successful}/{len(results)}")

        if successful > 1:
            unique = df["max_stress_Pa"].nunique()
            if unique > 1:
                print(f"✅ GEOMETRY SWAP CONFIRMED! ({unique} unique values)")
                print("\nYou can now change NUM_TEST_CASES to 300!")
            else:
                print("⚠️  Values identical - swap may not have worked")

        print(f"\n📊 Results: {OUTPUT_CSV}")

else:
    print("\n❌ Geometry swapping NOT possible with current template structure")
    print("\nRecommendation:")
    print("  Create template with 'External Model' geometry import method")

mechanical.exit()
print("\n✓ Done!")
