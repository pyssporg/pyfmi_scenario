"""Package a scenario and simulate it with FMPy."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    import fmpy
except ImportError:
    print(
        "example 04 needs fmpy; install the dev extra with "
        '`pip install -e ".[dev]"`',
        file=sys.stderr,
    )
    raise SystemExit(1) from None

from pyfmu_scenario import (
    PARAMETER_NAME,
    parse_scenario,
    serialize_scenario,
)
from pyfmu_scenario.packaging import package_scenario

SCENARIO_TEXT = """\
Alt;L;0.0,0.0;10.0,1000.0
gear;ZOH;0.0,0.0;4.0,1.0;8.0,2.0
mode;NN;0.0,0.0;10.0,3.0
"""
STOP_TIME = 10.0
OUTPUT_INTERVAL = 0.5
OUT = Path(__file__).resolve().parent / "out"


def main() -> None:
    scenario = parse_scenario(SCENARIO_TEXT)
    OUT.mkdir(parents=True, exist_ok=True)
    fmu = package_scenario(scenario, OUT / "scenario.fmu")

    result = fmpy.simulate_fmu(
        str(fmu),
        start_time=0.0,
        stop_time=STOP_TIME,
        output_interval=OUTPUT_INTERVAL,
        output=list(scenario.names),
        start_values={PARAMETER_NAME: serialize_scenario(scenario)},
    )

    names = result.dtype.names
    with (OUT / "results.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.writer(stream)
        writer.writerow(names)
        for row in result:
            writer.writerow([row[name] for name in names])

    print(f"FMU: {fmu}")
    print(f"CSV: {OUT / 'results.csv'} ({len(result)} rows)")
    print(" ".join(f"{name:>8}" for name in names))
    for index in (0, len(result) // 2, len(result) - 1):
        row = result[index]
        print(" ".join(f"{row[name]:8.4f}" for name in names))

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; skipping outputs.png")
        return

    figure, axes = plt.subplots()
    for name in scenario.names:
        axes.plot(result["time"], result[name], label=name)
    axes.set_xlabel("time / s")
    axes.legend()
    figure.tight_layout()
    figure.savefig(OUT / "outputs.png")
    print(f"plot: {OUT / 'outputs.png'}")


if __name__ == "__main__":
    main()
