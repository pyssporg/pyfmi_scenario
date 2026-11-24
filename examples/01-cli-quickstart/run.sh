#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="build/examples/01-cli-quickstart"

usage() {
    echo "usage: run.sh [--out DIR]" >&2
    exit 2
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --out) [[ $# -ge 2 ]] || usage; OUT="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

mkdir -p "$OUT"

python3 -m pyfmi_scenario package --scenario "$HERE/scenario.txt" \
    --output "$OUT/scenario.fmu"
python3 -m pyfmi_scenario ssv --scenario "$HERE/scenario.txt" \
    --output "$OUT/scenario.ssv"
python3 -m pyfmi_scenario run --fmu "$OUT/scenario.fmu" --output "$OUT/results.csv"
