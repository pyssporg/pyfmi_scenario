"""Build a scenario in Python, package it, and inspect the FMU."""

from __future__ import annotations

import math
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from pyfmu_scenario import (
    DEFAULT_GUID,
    Interpolation,
    Sample,
    Scenario,
    Series,
    parse_scenario,
    serialize_scenario,
)
from pyfmu_scenario.packaging import package_scenario

CUSTOM_GUID = "0f8fad5b-d9cb-469f-a165-70867728950e"
OUT = Path(__file__).resolve().parent / "out"


def main() -> None:
    sine = tuple(
        Sample(time=0.5 * index, value=math.sin(0.5 * index))
        for index in range(21)
    )
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

    text = serialize_scenario(scenario)
    assert parse_scenario(text) == scenario
    print("Canonical scenario text:")
    print(text)

    OUT.mkdir(parents=True, exist_ok=True)
    fmu = package_scenario(scenario, OUT / "scenario.fmu", guid=CUSTOM_GUID)

    with zipfile.ZipFile(fmu) as archive:
        entries = archive.namelist()
        root = ET.fromstring(archive.read("modelDescription.xml"))

    model_name = root.attrib["modelName"]
    guid = root.attrib["guid"]
    variables = [
        variable.attrib["name"] for variable in root.iter("ScalarVariable")
    ]

    print(f"FMU: {fmu}")
    print(f"model name: {model_name}")
    print(f"GUID: {guid} (default: {DEFAULT_GUID})")
    print(f"variables: {', '.join(variables)}")
    print(f"archive entries: {', '.join(entries)}")

    assert guid == CUSTOM_GUID
    assert model_name == "scenario"
    for name in scenario.names:
        assert name in variables


if __name__ == "__main__":
    main()
