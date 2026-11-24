from pathlib import Path

from pyfmi_scenario.grammar import parse_scenario, serialize_scenario
from pyfmi_scenario.model import (
    DEFAULT_EXPERIMENT,
    DEFAULT_GUID,
    MODEL_IDENTIFIER,
    MODEL_NAME,
    PARAMETER_NAME,
    build_component,
    build_reduction,
    build_variables,
)

DATA = Path(__file__).resolve().parents[1] / "data"
SCENARIO = parse_scenario(
    (DATA / "scenario.txt").read_text(encoding="utf-8").strip()
)


def test_reduction_identity_is_the_scenario_direct_fmu():
    reduction = build_reduction(SCENARIO)

    assert reduction.components == (build_component(SCENARIO),)
    assert reduction.identity.system == MODEL_NAME
    assert reduction.identity.direct is True
    assert reduction.identity.guid == DEFAULT_GUID
    assert reduction.identity.model_name(MODEL_IDENTIFIER) == MODEL_NAME
    assert reduction.package == ""
    assert reduction.root is None
    assert reduction.experiment == DEFAULT_EXPERIMENT


def test_custom_guid_is_kept_verbatim():
    guid = "01234567-89ab-cdef-0123-456789abcdef"

    reduction = build_reduction(SCENARIO, guid=guid)

    assert reduction.identity.guid == guid


def test_value_references_and_indices():
    variables = build_variables(SCENARIO)
    parameter, *outputs = variables

    assert parameter.name == PARAMETER_NAME
    assert parameter.type_name == "String"
    assert parameter.causality == "parameter"
    assert parameter.variability == "tunable"
    assert parameter.value_reference == 0
    assert parameter.index == 1

    assert [variable.name for variable in outputs] == list(SCENARIO.names)
    assert [variable.value_reference for variable in outputs] == [1, 2, 3, 4, 5]
    assert [variable.index for variable in outputs] == [2, 3, 4, 5, 6]
    assert all(variable.type_name == "Real" for variable in outputs)
    assert all(variable.causality == "output" for variable in outputs)
    assert all(variable.variability is None for variable in outputs)
    assert all(variable.start is None for variable in outputs)


def test_parameter_start_is_the_canonical_scenario_text():
    parameter = build_variables(SCENARIO)[0]

    assert parameter.start_text == serialize_scenario(SCENARIO)
    assert parameter.start == parameter.start_text
    assert parse_scenario(parameter.start_text) == SCENARIO


def test_parameter_start_can_be_overridden():
    parameter = build_variables(SCENARIO, parameter_start="x;ZOH;0,1")[0]

    assert parameter.start_text == "x;ZOH;0,1"


def test_component_is_named_by_the_model_identifier():
    component = build_component(SCENARIO)

    assert component.name == MODEL_IDENTIFIER
    assert component.outputs == build_variables(SCENARIO)[1:]
    assert component.vr_count == len(SCENARIO.series) + 1
    assert [field.name for field in component.parameters] == [PARAMETER_NAME]
    assert component.parameters[0].type_name == "String"
    assert [port.name for port in component.ports] == list(SCENARIO.names)
    assert component.variables[0].start is None
    assert component.variables[0].start_text is None


def test_outputs_are_mutually_distinct():
    component = build_component(SCENARIO)

    assert len({variable.name for variable in component.variables}) == len(
        component.variables
    )
    assert len(
        {variable.value_reference for variable in component.variables}
    ) == len(component.variables)


def test_build_variables_rejects_nothing_for_a_valid_scenario():
    # A regression guard: the fixture has five output series.
    assert len(build_variables(SCENARIO)) == 6
