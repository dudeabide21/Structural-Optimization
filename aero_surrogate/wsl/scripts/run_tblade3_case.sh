
#!/usr/bin/env bash
set -eu

# Usage: bash run_tblade3_case.sh /path/to/case_000X

CASE_DIR="${1:-}"
if [ -z "$CASE_DIR" ]; then
  echo "ERROR: provide case dir"
  echo "Usage: $0 /path/to/case_000X"
  exit 1
fi

if [ ! -d "$CASE_DIR" ]; then
  echo "ERROR: case dir not found: $CASE_DIR"
  exit 1
fi

INPUT_FILE="$CASE_DIR/input.dat"
if [ ! -f "$INPUT_FILE" ]; then
  echo "ERROR: input.dat missing in $CASE_DIR"
  exit 1
fi

# --- SET THIS to your compiled tblade3 binary ---
TBL3_BIN="$HOME/projects/tblade3/bin/tblade3"

if [ ! -x "$TBL3_BIN" ]; then
  echo "ERROR: tblade3 binary not executable: $TBL3_BIN"
  exit 1
fi

# --- Baseline aux files (copied from case_0001) ---
ROOT_CASES="$(cd "$CASE_DIR/../.." && pwd)"
BASELINE_CASE="$ROOT_CASES/case_0001"

# required aux file
AUX="spancontrolinputs.input.dat"
if [ ! -f "$CASE_DIR/$AUX" ]; then
  if [ -f "$BASELINE_CASE/$AUX" ]; then
    cp -f "$BASELINE_CASE/$AUX" "$CASE_DIR/$AUX"
  else
    echo "ERROR: missing aux $AUX in $CASE_DIR and baseline $BASELINE_CASE"
    exit 1
  fi
fi

# run
echo "Running tblade3 in: $CASE_DIR"
(
  cd "$CASE_DIR"
  rm -f T-Blade3_run.log
  "$TBL3_BIN" < input.dat > T-Blade3_run.log 2>&1
)

# sanity check
SEC_COUNT="$(ls "$CASE_DIR"/sec*.dat 2>/dev/null | wc -l || true)"
echo "sec*.dat count: $SEC_COUNT"
if [ "$SEC_COUNT" -lt 5 ]; then
  echo "ERROR: too few section files. Check $CASE_DIR/T-Blade3_run.log"
  exit 2
fi

echo "OK: generated $SEC_COUNT sections"
EOF
