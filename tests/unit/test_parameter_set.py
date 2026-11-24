from pathlib import Path

from pyssp_standard import SSV

from pyfmi_scenario.grammar import parse_scenario, serialize_scenario
from pyfmi_scenario.parameter_set import write_parameter_set

DATA = Path(__file__).resolve().parents[1] / "data"
SCENARIO = parse_scenario(
    (DATA / "scenario.txt").read_text(encoding="utf-8").strip()
)


def test_parameter_set_binds_the_scenario_text(tmp_path):
    path = write_parameter_set(tmp_path / "scenario.ssv", SCENARIO)

    assert path == tmp_path / "scenario.ssv"
    with SSV(path, mode="r") as parameter_set:
        parameters = parameter_set.parameters_by_name()

    assert set(parameters) == {"scenario_input"}
    parameter = parameters["scenario_input"]
    assert parameter.type_name == "String"
    assert parameter.attributes["value"] == serialize_scenario(SCENARIO)
    assert parse_scenario(parameter.attributes["value"]) == SCENARIO


def test_raw_text_is_written_verbatim(tmp_path):
    path = write_parameter_set(tmp_path / "raw.ssv", "x;ZOH;0,1")

    with SSV(path, mode="r") as parameter_set:
        parameters = parameter_set.parameters_by_name()

    assert parameters["scenario_input"].attributes["value"] == "x;ZOH;0,1"
