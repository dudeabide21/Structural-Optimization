import os
import Ansys.Mechanical.DataModel.Enums as Enums

# === CONFIGURATION ===
out_dir = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\fea_results"
csv_p = os.path.join(out_dir, "fea_results.csv")

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

try:
    # 1. Access Data Model
    model = ExtAPI.DataModel.Project.Model
    analysis = model.Analyses[0]
    solution = analysis.Solution

    # 2. Case Label
    try:
        label = case_label
    except:
        label = "manual_test"

    # 3. Force Evaluation (Safely)
    solution.EvaluateAllResults()

    # 4. Extract Stress (Search by Category)
    max_stress = 0.0
    # This finds Equivalent Stress objects regardless of name
    stress_results = [
        c
        for c in solution.Children
        if c.DataModelObjectCategory == Enums.DataModelObjectCategory.EquivalentStress
    ]

    if len(stress_results) > 0:
        # Get the first result found
        res = stress_results[0]
        # We use .MaximumValue (Data Series) for higher reliability
        max_stress = res.Maximum.Value

    # 5. Extract Geometry Data
    total_vol = 0.0
    total_mass = 0.0
    # Get all body objects
    bodies = model.GetChildren(Enums.DataModelObjectCategory.Body, True)
    for b in bodies:
        total_vol = b.Volume.Value
        total_mass = b.Mass.Value

    # 6. WRITE TO FILE (Old School method for IronPython compatibility)
    f = open(csv_p, "a")
    # If file doesn't exist or is empty, add header
    if not os.path.exists(csv_p) or os.path.getsize(csv_p) == 0:
        f.write("case,stress_Pa,vol_m3,mass_kg\n")

    line = "{0},{1},{2},{3}\n".format(label, max_stress, total_vol, total_mass)
    f.write(line)
    f.flush()
    f.close()

    print("SUCCESS: Result recorded for " + label)

except Exception as e:
    # Catching the error and printing it to the console is vital
    print("CRITICAL ERROR: " + str(e))
