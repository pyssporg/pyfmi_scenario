#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="$HERE/out"
mkdir -p "$OUT"

if command -v pyfmu-scenario >/dev/null 2>&1; then
    PYFMU=(pyfmu-scenario)
else
    # Source checkout without an installed console script.
    export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
    PYFMU=("${PYTHON:-python3}" -m pyfmu_scenario)
fi

"${PYFMU[@]}" package --scenario "$HERE/scenario.txt" \
    --output "$OUT/scenario.fmu"
"${PYFMU[@]}" ssv --scenario "$HERE/scenario.txt" \
    --output "$OUT/scenario.ssv"
"${PYFMU[@]}" run --fmu "$OUT/scenario.fmu" --output "$OUT/results.csv"
