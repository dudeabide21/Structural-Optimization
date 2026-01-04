import os
import Ansys.Mechanical.DataModel.Enums as Enums

# === CONFIGURATION ===
# Set your Material Yield Strength in Pascals (e.g., 250 MPa = 250e6)
yield_strength = 1.1e9
out_dir = r"C:\Users\dipes\OneDrive\Documents\Machine Learning\Python\Structural Optimization\aero_surrogate\fea_results"
csv_p = os.path.join(out_dir, "margin_of_safety_results.csv")

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

try:
    # 1. Access Data Model
    model = ExtAPI.DataModel.Project.Model
    analysis = model.Analyses[0]
    solution = analysis.Solution

    # 2. Case Label (Injected by Workbench Journal)
    try:
        label = case_label
    except:
        label = "manual_test"

    # 3. Extract Max Stress
    max_stress = 0.0
    stress_results = [c for c in solution.Children if c.DataModelObjectCategory == Enums.DataModelObjectCategory.EquivalentStress]

    if len(stress_results) > 0:
        res = stress_results[0]
        # Ensure result is calculated
        if res.ObjectState != Enums.ObjectState.Solved:
            res.EvaluateAllResults()
        max_stress = res.Maximum.Value
    else:
        raise Exception("Equivalent Stress object not found in tree.")

    # 4. Calculate Margin of Safety
    # Formula: MoS = (Yield / (1.1 * Max_Stress)) - 1
    if max_stress > 0:
        design_load = 1.1 * max_stress
        margin_of_safety = (yield_strength / design_load) - 1.0
    else:
        margin_of_safety = 999.0 # Placeholder for zero-stress state

    # 5. WRITE TO CSV
    file_exists = os.path.exists(csv_p)
    f = open(csv_p, "a")
    
    if not file_exists or os.path.getsize(csv_p) == 0:
        f.write("case,max_stress_Pa,yield_strength_Pa,margin_of_safety\n")

    line = "{0},{1},{2},{3}\n".format(label, max_stress, yield_strength, margin_of_safety)
    f.write(line)
    f.flush()
    f.close()

    print("SUCCESS: Result recorded for {0}. MoS: {1}".format(label, margin_of_safety))

except Exception as e:
    print("CRITICAL ERROR: " + str(e))
