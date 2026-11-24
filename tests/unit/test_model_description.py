import os
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pyfmi_scenario.grammar import parse_scenario
from pyfmi_scenario.model import (
    AUTHOR,
    DEFAULT_GUID,
    GENERATION_TOOL,
    MODEL_IDENTIFIER,
    MODEL_NAME,
    PARAMETER_NAME,
    VERSION,
)
from pyfmi_scenario.model_description import build_model_description

DATA = Path(__file__).resolve().parents[1] / "data"
SCENARIO = parse_scenario(
    (DATA / "scenario.txt").read_text(encoding="utf-8").strip()
)

# The reference FMU predates this producer's identity metadata. Structure and
# every other attribute must match; these two values are the deliberate rename.
FIXTURE_DIFFERENCES = {
    "author": (AUTHOR, "scenario_fmu"),
    "generationTool": (GENERATION_TOOL, "scenario_fmu"),
}


def _fixture_path() -> Path:
    override = os.environ.get("PYFMI_SCENARIO_FIXTURE")
    relative = Path(
        "repos/ssp_references/models/fmu/scenario/fmu/modelDescription.xml"
    )
    candidates = [Path(override)] if override else []
    candidates.extend(parent / relative for parent in Path(__file__).parents)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    pytest.skip("ssp_references scenario fixture is not available")


def _parse(xml_text: str) -> ET.Element:
    return ET.fromstring(xml_text)


def test_root_attributes_match_the_fmu_identity():
    root = _parse(build_model_description(SCENARIO))

    assert root.tag == "fmiModelDescription"
    assert root.attrib["fmiVersion"] == "2.0"
    assert root.attrib["modelName"] == MODEL_NAME
    assert root.attrib["guid"] == DEFAULT_GUID
    assert root.attrib["author"] == AUTHOR
    assert root.attrib["version"] == VERSION
    assert root.attrib["generationTool"] == GENERATION_TOOL
    assert root.attrib["variableNamingConvention"] == "structured"
    assert root.attrib["numberOfEventIndicators"] == "0"
    assert "generationDateAndTime" not in root.attrib


def test_co_simulation_capabilities():
    root = _parse(build_model_description(SCENARIO))
    capabilities = root.find("CoSimulation")

    assert capabilities is not None
    assert dict(capabilities.attrib) == {
        "modelIdentifier": MODEL_IDENTIFIER,
        "canHandleVariableCommunicationStepSize": "true",
        "canInterpolateInputs": "false",
        "needsExecutionTool": "false",
        "canBeInstantiatedOnlyOncePerProcess": "false",
        "canNotUseMemoryManagementFunctions": "true",
        "providesDirectionalDerivative": "false",
    }


def test_default_experiment():
    root = _parse(build_model_description(SCENARIO))
    experiment = root.find("DefaultExperiment")

    assert experiment is not None
    assert dict(experiment.attrib) == {
        "startTime": "0.0",
        "stopTime": "10.0",
        "tolerance": "0.0001",
    }


def test_variables_and_parameter_start_text():
    root = _parse(build_model_description(SCENARIO))
    variables = root.findall("./ModelVariables/ScalarVariable")

    assert len(variables) == len(SCENARIO.series) + 1
    parameter = variables[0]
    assert parameter.attrib == {
        "name": PARAMETER_NAME,
        "valueReference": "0",
        "causality": "parameter",
        "variability": "tunable",
    }
    parameter_type = next(iter(parameter))
    assert parameter_type.tag == "String"
    assert parse_scenario(parameter_type.attrib["start"]) == SCENARIO

    names = [variable.attrib["name"] for variable in variables[1:]]
    assert names == list(SCENARIO.names)
    assert [
        variable.attrib["valueReference"] for variable in variables[1:]
    ] == ["1", "2", "3", "4", "5"]
    for variable in variables[1:]:
        assert variable.attrib["causality"] == "output"
        assert "variability" not in variable.attrib
        assert len(variable) == 1
        assert variable[0].tag == "Real"
        assert variable[0].attrib == {}


def test_model_structure_lists_output_indices():
    root = _parse(build_model_description(SCENARIO))
    structure = root.find("ModelStructure")

    assert structure is not None
    assert [child.tag for child in structure] == ["Outputs"]
    outputs = structure.find("Outputs")
    assert outputs is not None
    assert [
        dict(unknown.attrib) for unknown in outputs.findall("Unknown")
    ] == [{"index": str(index)} for index in range(2, 7)]


def test_custom_guid_is_reflected():
    guid = "01234567-89ab-cdef-0123-456789abcdef"

    root = _parse(build_model_description(SCENARIO, guid=guid))

    assert root.attrib["guid"] == guid


def test_matches_the_reference_fixture_structurally():
    reference = ET.parse(_fixture_path()).getroot()
    ours = _parse(build_model_description(SCENARIO))

    assert ours.tag == reference.tag
    assert [child.tag for child in ours] == [
        child.tag for child in reference
    ]

    ours_attributes = dict(ours.attrib)
    reference_attributes = dict(reference.attrib)
    assert set(ours_attributes) == set(reference_attributes)
    for name, (expected, reference_value) in FIXTURE_DIFFERENCES.items():
        assert ours_attributes[name] == expected
        assert reference_attributes[name] == reference_value
    for name, value in reference_attributes.items():
        if name not in FIXTURE_DIFFERENCES:
            assert ours_attributes[name] == value

    for section in ("CoSimulation", "DefaultExperiment"):
        ours_section = ours.find(section)
        reference_section = reference.find(section)
        assert ours_section is not None
        assert reference_section is not None
        assert dict(ours_section.attrib) == dict(reference_section.attrib)

    ours_variables = ours.findall("./ModelVariables/ScalarVariable")
    reference_variables = reference.findall("./ModelVariables/ScalarVariable")
    assert len(ours_variables) == len(reference_variables)
    for ours_variable, reference_variable in zip(
        ours_variables, reference_variables
    ):
        assert dict(ours_variable.attrib) == dict(reference_variable.attrib)
        assert [child.tag for child in ours_variable] == [
            child.tag for child in reference_variable
        ]
        for ours_type, reference_type in zip(ours_variable, reference_variable):
            assert dict(ours_type.attrib) == dict(reference_type.attrib)

    ours_structure = ours.find("ModelStructure")
    reference_structure = reference.find("ModelStructure")
    assert ours_structure is not None
    assert reference_structure is not None
    assert [child.tag for child in ours_structure] == [
        child.tag for child in reference_structure
    ]
    assert [
        dict(unknown.attrib)
        for unknown in ours_structure.findall("./Outputs/Unknown")
    ] == [
        dict(unknown.attrib)
        for unknown in reference_structure.findall("./Outputs/Unknown")
    ]
