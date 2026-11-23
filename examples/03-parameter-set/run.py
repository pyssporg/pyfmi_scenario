"""Write the scenario_input binding as an SSP 1.0 parameter set."""

from __future__ import annotations

import argparse
from pathlib import Path

from pyfmu_scenario import parse_scenario, write_parameter_set

SCENARIO_PATH = Path(__file__).resolve().parents[1] / "01-cli-quickstart" / "scenario.txt"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/examples/03-parameter-set"))
    args = parser.parse_args(argv)

    scenario = parse_scenario(SCENARIO_PATH.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)
    print(write_parameter_set(args.out / "scenario.ssv", scenario, name="ScenarioSet"))


if __name__ == "__main__":
    main()
