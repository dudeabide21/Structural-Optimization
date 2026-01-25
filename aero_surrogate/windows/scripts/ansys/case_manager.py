"""
PyMechanical Complete Script - 3 Test Cases
Fixed for ANSYS 2025 R2 (pre-SP03) security issue
"""

import os
import pandas as pd
from pathlib import Path

# Disable security for ANSYS 2025 R2
os.environ['ANSYS_MECHANICAL_NO_SECURITY'] = '1'

print("Importing PyMechanical...")
try:
    import ansys.mechanical.core as pymechanical
    print("✓ PyMechanical imported\n")
except ImportError:
    print("❌ ERROR: PyMechanical not installed")
    print("Install it with: pip install ansys-mechanical-core")
    exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================
STEP_FOLDER = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\FEA\cases"
TEMPLATE_PROJECT = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\workbench\blade_body.mechdat.wbpj"
OUTPUT_CSV = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\fea_results\fea_results.csv"

NUM_TEST_CASES = 3

print("Configuration:")
print(f"  STEP folder: {STEP_FOLDER}")
print(f"  Template:    {TEMPLATE_PROJECT}")
print(f"  Output CSV:  {OUTPUT_CSV}")
print(f"  Test cases:  {NUM_TEST_CASES}\n")

# ============================================================================
# VALIDATION
# ============================================================================
print("Validating paths...")

if not Path(TEMPLATE_PROJECT).exists():
    print(f"❌ ERROR: Template not found at:\n   {TEMPLATE_PROJECT}")
    exit(1)
print(f"✓ Template found")

if not Path(STEP_FOLDER).exists():
    print(f"❌ ERROR: STEP folder not found at:\n   {STEP_FOLDER}")
    exit(1)
print(f"✓ STEP folder found")

step_files = sorted(Path(STEP_FOLDER).glob("*.step"))[:NUM_TEST_CASES]
if len(step_files) == 0:
    print(f"❌ ERROR: No STEP files found in:\n   {STEP_FOLDER}")
    exit(1)

print(f"✓ Found {len(step_files)} STEP files:")
for i, f in enumerate(step_files, 1):
    print(f"   {i}. {f.name}")

Path(OUTPUT_CSV).parent.mkdir(parents=True, exist_ok=True)
print(f"✓ Output directory ready\n")

# ============================================================================
# LAUNCH MECHANICAL
# ============================================================================
print("=" * 80)
print("LAUNCHING ANSYS MECHANICAL (EMBEDDED MODE)")
print("=" * 80)
print("This may take 1-2 minutes...\n")

print("⚠️  Using embedded mode instead of gRPC (Student version compatibility)")

try:
    # Use embedded mode which doesn't require gRPC
    from ansys.mechanical.core import App
    
    print("Launching embedded Mechanical instance...")
    mechanical = App()
    print(f"✅ Mechanical launched successfully!")
    print(f"   Version: {mechanical}")
    print()
    
except Exception as e:
    print(f"❌ Failed to launch Mechanical (embedded mode): {e}\n")
    
    # Fallback: Try with explicit version
    print("Trying alternative launch method...")
    try:
        mechanical = App(version=252)
        print(f"✅ Mechanical launched successfully!")
        print(f"   Version: {mechanical}\n")
    except Exception as e2:
        print(f"❌ Also failed: {e2}\n")
        print("\nTroubleshooting:")
        print("1. Make sure ANSYS Student 2025 R2 is properly installed")
        print("2. Try running Python as administrator")
        print("3. Check if ansys-mechanical-env is installed: pip install ansys-mechanical-env")
        print("4. Restart your computer and try again")
        exit(1)

results = []

# ============================================================================
# PROCESS EACH CASE
# ============================================================================
for idx, step_file in enumerate(step_files, 1):
    print("=" * 80)
    print(f"CASE {idx}/{len(step_files)}: {step_file.name}")
    print("=" * 80)
    
    try:
        # Step 1: Open template
        print(f"\n[1/6] Opening template project...")
        mechanical.open(TEMPLATE_PROJECT)
        print("✓ Template opened")
        
        # Step 2: Import geometry
        print(f"[2/6] Importing geometry: {step_file.name}")
        geometry = mechanical.DataModel.Project.Model.Geometry
        geometry_import = geometry.AddGeometryImport()
        geometry_import_group = geometry_import.AddGeometryImportGroup()
        
        import_format = mechanical.Ansys.Mechanical.DataModel.Enums.GeometryImportPreference.Format.Automatic
        import_preferences = mechanical.Ansys.ACT.Mechanical.Utilities.GeometryImportPreferences()
        import_preferences.ProcessNamedSelections = True
        import_preferences.ProcessCoordinateSystems = True
        
        geometry_import_group.Import(str(step_file), import_format, import_preferences)
        print("✓ Geometry imported")
        
        # Step 3: Generate mesh
        print(f"[3/6] Generating mesh...")
        mesh = mechanical.DataModel.Project.Model.Mesh
        mesh.GenerateMesh()
        print(f"✓ Mesh: {mesh.Nodes} nodes, {mesh.Elements} elements")
        
        # Step 4: Solve
        print(f"[4/6] Solving FEA...")
        analysis = mechanical.DataModel.Project.Model.Analyses[0]
        solution = analysis.Solution
        solution.Solve(True)
        print("✓ Solution complete")
        
        # Step 5: Extract results
        print(f"[5/6] Extracting results...")
        
        # Find stress result
        stress_result = None
        for child in solution.Children:
            if hasattr(child, 'Maximum') and 'Stress' in str(type(child)):
                stress_result = child
                break
        
        if stress_result is None:
            raise Exception("No stress result found in solution")
        
        max_stress = float(stress_result.Maximum)
        volume = float(geometry.Volume)
        mass = float(geometry.Mass)
        
        # Step 6: Store results
        print(f"[6/6] Storing results...")
        results.append({
            'case_label': step_file.stem,
            'step_file': str(step_file),
            'max_von_mises_Pa': max_stress,
            'volume_m3': volume,
            'mass_kg': mass,
            'status': 'SUCCESS'
        })
        
        print(f"\n✅ CASE {idx} COMPLETE:")
        print(f"   Max von Mises: {max_stress:.2e} Pa")
        print(f"   Volume:        {volume:.6e} m³")
        print(f"   Mass:          {mass:.6e} kg")
        
    except Exception as e:
        print(f"\n❌ CASE {idx} FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        results.append({
            'case_label': step_file.stem,
            'step_file': str(step_file),
            'max_von_mises_Pa': None,
            'volume_m3': None,
            'mass_kg': None,
            'status': f'FAILED: {str(e)}'
        })
    
    # Save progress after each case
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n💾 Progress saved\n")

# ============================================================================
# CLEANUP & SUMMARY
# ============================================================================
print("=" * 80)
print("CLOSING MECHANICAL")
print("=" * 80)
mechanical.exit()
print("✓ Mechanical closed\n")

# Final summary
print("=" * 80)
print("TEST RUN COMPLETE - SUMMARY")
print("=" * 80)

df = pd.DataFrame(results)
successful = df[df['status'] == 'SUCCESS']
failed = df[df['status'] != 'SUCCESS']

print(f"\n✅ Successful: {len(successful)}/{len(results)}")
print(f"❌ Failed:     {len(failed)}/{len(results)}")

if len(successful) > 0:
    print("\nResults Preview:")
    print(successful[['case_label', 'max_von_mises_Pa', 'volume_m3', 'mass_kg']].to_string(index=False))

print(f"\n📊 Full results saved to:\n   {OUTPUT_CSV}")

if len(successful) == len(results):
    print("\n🎉 ALL TESTS PASSED! Ready to run full 300 cases.")
    print("\nTo run all 300 cases:")
    print("  1. Change NUM_TEST_CASES = 3 to NUM_TEST_CASES = 300")
    print("  2. Run this script again")
else:
    print("\n⚠️  Some cases failed. Review errors above.")

print("=" * 80)