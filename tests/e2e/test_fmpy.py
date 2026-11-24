"""End-to-end: fmpy drives the packaged FMU through the scenario grammar."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from pyfmi_scenario.grammar import parse_scenario, serialize_scenario
from pyfmi_scenario.model import PARAMETER_NAME
from pyfmi_scenario.packaging import package_scenario
from pyfmi_scenario.series import evaluate_scenario

fmpy = pytest.importorskip("fmpy")

pytestmark = pytest.mark.e2e

DATA = Path(__file__).resolve().parents[1] / "data"
SCENARIO = parse_scenario((DATA / "scenario.txt").read_text(encoding="utf-8"))
BASELINE = DATA / "scenario_baseline.csv"


@pytest.fixture(scope="module")
def fmu(tmp_path_factory: pytest.TempPathFactory) -> Path:
    directory = tmp_path_factory.mktemp("scenario-e2e")
    return package_scenario(SCENARIO, directory / "scenario.fmu")


def _start_value(fmu: Path) -> str:
    description = fmpy.read_model_description(str(fmu))
    parameter = next(
        variable
        for variable in description.modelVariables
        if variable.name == PARAMETER_NAME
    )
    assert isinstance(parameter.start, str)
    return parameter.start


def _outputs(fmu: Path) -> list[str]:
    description = fmpy.read_model_description(str(fmu))
    return [
        variable.name
        for variable in description.modelVariables
        if variable.causality == "output"
    ]


def test_model_description_identity(fmu: Path) -> None:
    description = fmpy.read_model_description(str(fmu))

    assert description.modelName == "scenario"
    assert description.modelIdentifier == "scenario"
    assert [variable.name for variable in description.modelVariables] == [
        PARAMETER_NAME,
        *SCENARIO.names,
    ]


def test_baseline_matches_the_reference_series(fmu: Path) -> None:
    outputs = _outputs(fmu)
    result = fmpy.simulate_fmu(
        str(fmu),
        start_time=0.0,
        stop_time=1200.0,
        output_interval=2.0,
        output=outputs,
        start_values={PARAMETER_NAME: _start_value(fmu)},
    )

    with BASELINE.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))

    assert len(result) == len(rows)
    for index, row in enumerate(rows):
        assert result["time"][index] == pytest.approx(
            float(row["time"]), abs=1e-9
        )
        for name in outputs:
            assert result[name][index] == pytest.approx(
                float(row[name]), rel=1e-9, abs=1e-9
            ), f"{name} at t={row['time']}"


def test_modified_scenario_text_parameterizes_the_runtime(fmu: Path) -> None:
    modified_text = (
        "Alt;L;0.0,0.0;20.0,100.0\n"
        "Mach;L;0.0,0.0;20.0,2.0\n"
        "heat_load;ZOH;0.0,7.0;10.0,9.0\n"
        "Wgt_On_Whl;ZOH;0.0,0.5\n"
        "Aircraft_state;NN;0.0,1.0;20.0,3.0"
    )
    modified = parse_scenario(modified_text)
    assert serialize_scenario(modified) == modified_text

    outputs = _outputs(fmu)
    result = fmpy.simulate_fmu(
        str(fmu),
        start_time=0.0,
        stop_time=20.0,
        output_interval=2.0,
        output=outputs,
        start_values={PARAMETER_NAME: modified_text},
    )

    for index in range(len(result)):
        time = float(result["time"][index])
        expected = evaluate_scenario(modified, time)
        for name in outputs:
            assert result[name][index] == pytest.approx(
                expected[name], rel=1e-12, abs=1e-12
            ), f"{name} at t={time}"


@pytest.mark.parametrize(
    "invalid_text",
    [
        pytest.param(
            "Alt;C;0.0,0.0;20.0,100.0\n"
            "Mach;L;0.0,0.0;20.0,2.0\n"
            "heat_load;ZOH;0.0,7.0\n"
            "Wgt_On_Whl;ZOH;0.0,0.5\n"
            "Aircraft_state;ZOH;0.0,1.0",
            id="cubic-unsupported",
        ),
        pytest.param(
            "Unknown;L;0.0,0.0;20.0,100.0\n"
            "Mach;L;0.0,0.0;20.0,2.0\n"
            "heat_load;ZOH;0.0,7.0\n"
            "Wgt_On_Whl;ZOH;0.0,0.5\n"
            "Aircraft_state;ZOH;0.0,1.0",
            id="unknown-name",
        ),
        pytest.param(
            "Alt;L;0.0,0.0;20.0,100.0\n"
            "Mach;L;0.0,0.0;20.0,2.0\n"
            "heat_load;ZOH;0.0,7.0\n"
            "Wgt_On_Whl;ZOH;0.0,0.5",
            id="missing-output",
        ),
    ],
)
def test_runtime_rejects_an_invalid_parameter(
    fmu: Path, invalid_text: str
) -> None:
    outputs = _outputs(fmu)

    with pytest.raises(fmpy.fmi1.FMICallException):
        fmpy.simulate_fmu(
            str(fmu),
            start_time=0.0,
            stop_time=1.0,
            output_interval=1.0,
            output=outputs,
            start_values={PARAMETER_NAME: invalid_text},
        )

