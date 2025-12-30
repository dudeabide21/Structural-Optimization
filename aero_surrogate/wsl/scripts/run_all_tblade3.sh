#!/bin/bash

# Root can be modified to point to the correct directory
ROOT="/mnt/c/Users/dipes/OneDrive/Documents/Machine Learning/Python/Structural Optimization/aero_surrogate/wsl/fea_cases"

for i in $(seq -w 0002 0300); do
    CASE="$ROOT/case_$i"
    echo "Running T-Blade3 for $CASE"
    
    if [ -f "$CASE/input.dat" ]; then
        $HOME/projects/tblade3/bin/tblade3 < "$CASE/input.dat" > "$CASE/T-Blade3_run.log" 2>&1
        echo "Finished case_$i"
    else
        echo "Missing input.dat in case_$i"
    fi
done

echo "DONE generating T-Blade3 outputs."
