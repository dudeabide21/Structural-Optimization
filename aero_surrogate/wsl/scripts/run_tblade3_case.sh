#!/bin/bash
# Usage: ./run_tblade3_case.sh /path/to/case_dir

# 1 argument: directory containing input.dat
CASE_DIR="$1"

if [ -z "$CASE_DIR" ]; then
    echo "Usage: $0 /path/to/case_dir"
    exit 1
fi

if [ ! -d "$CASE_DIR" ]; then
    echo "Error: directory '$CASE_DIR' does not exist."
    exit 1
fi

if [ ! -f "$CASE_DIR/input.dat" ]; then
    echo "Error: '$CASE_DIR/input.dat' not found."
    exit 1
fi

# Path to the T-Blade3 binary you built in WSL
TBL_BIN="$HOME/projects/tblade3/bin/tblade3"

if [ ! -x "$TBL_BIN" ]; then
    echo "Error: T-Blade3 binary '$TBL_BIN' not found or not executable."
    exit 1
fi

echo "[INFO] Running T-Blade3 in $CASE_DIR ..."
cd "$CASE_DIR"

# Run T-Blade3 and capture output in log.txt
"$TBL_BIN" input.dat > log.txt 2>&1

echo "[INFO] Finished. See log.txt in $CASE_DIR."
