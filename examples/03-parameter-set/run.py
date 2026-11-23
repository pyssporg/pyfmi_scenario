"""Write the scenario_input binding as an SSP 1.0 parameter set."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from pyfmu_scenario import (
    parse_scenario,
    serialize_scenario,
    write_parameter_set,
)

SSP1_NAMESPACE = "http://ssp-standard.org/SSP1/SystemStructureParameterValues"
HERE = Path(__file__).resolve().parent
SCENARIO_PATH = HERE.parent / "01-cli-quickstart" / "scenario.txt"


def main() -> None:
    scenario = parse_scenario(SCENARIO_PATH.read_text(encoding="utf-8"))
    out = HERE / "out"
    out.mkdir(parents=True, exist_ok=True)
    ssv = write_parameter_set(
        out / "scenario.ssv", scenario, name="ScenarioSet"
    )

    root = ET.parse(ssv).getroot()
    namespace = root.tag[1:].split("}", 1)[0]
    parameter = next(
        element
        for element in root.iter(f"{{{namespace}}}Parameter")
        if element.attrib.get("name") == "scenario_input"
    )
    value = next(iter(parameter)).attrib["value"]

    print(f"file: {ssv}")
    print(f"root: {root.tag}")
    print(f"namespace: {namespace}")
    print(f"scenario_input: {value!r}")

    assert namespace == SSP1_NAMESPACE
    assert root.tag == f"{{{SSP1_NAMESPACE}}}ParameterSet"
    assert root.attrib["name"] == "ScenarioSet"
    assert value == serialize_scenario(scenario)


if __name__ == "__main__":
    main()
