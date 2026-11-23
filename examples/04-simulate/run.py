"""Package a scenario and simulate it with FMPy."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import fmpy

from pyfmu_scenario import PARAMETER_NAME, parse_scenario, serialize_scenario
from pyfmu_scenario.packaging import package_scenario

SCENARIO_TEXT = """\
Alt;L;0.0,0.0;10.0,1000.0
gear;ZOH;0.0,0.0;4.0,1.0;8.0,2.0
mode;NN;0.0,0.0;10.0,3.0
"""
STOP_TIME = 10.0
OUTPUT_INTERVAL = 0.5


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/examples/04-simulate"))
    args = parser.parse_args(argv)

    scenario = parse_scenario(SCENARIO_TEXT)
    args.out.mkdir(parents=True, exist_ok=True)
    fmu = package_scenario(scenario, args.out / "scenario.fmu")

    result = fmpy.simulate_fmu(
        str(fmu),
        start_time=0.0,
        stop_time=STOP_TIME,
        output_interval=OUTPUT_INTERVAL,
        output=list(scenario.names),
        start_values={PARAMETER_NAME: serialize_scenario(scenario)},
    )

    names = result.dtype.names
    csv_path = args.out / "results.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(names)
        for row in result:
            writer.writerow([row[name] for name in names])

    print(fmu)
    print(csv_path)


if __name__ == "__main__":
    main()
