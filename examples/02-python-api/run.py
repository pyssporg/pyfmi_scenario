"""Build a scenario in Python and package it as an FMI 2.0 FMU."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from pyfmi_scenario import Interpolation, Sample, Scenario, Series
from pyfmi_scenario.packaging import package_scenario

CUSTOM_GUID = "0f8fad5b-d9cb-469f-a165-70867728950e"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("build/examples/02-python-api"))
    args = parser.parse_args(argv)

    sine = tuple(Sample(time=0.5 * index, value=math.sin(0.5 * index)) for index in range(21))
    scenario = Scenario(
        series=(
            Series("sine", Interpolation.LINEAR, sine),
            Series(
                "step",
                Interpolation.ZERO_ORDER_HOLD,
                (Sample(0.0, 0.0), Sample(5.0, 1.0)),
            ),
            Series(
                "mode",
                Interpolation.NEAREST_NEIGHBOUR,
                (Sample(0.0, 0.0), Sample(10.0, 3.0)),
            ),
        )
    )

    args.out.mkdir(parents=True, exist_ok=True)
    print(package_scenario(scenario, args.out / "scenario.fmu", guid=CUSTOM_GUID))


if __name__ == "__main__":
    main()
