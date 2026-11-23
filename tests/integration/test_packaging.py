"""A real CMake build produces the expected FMI 2.0 archive layout."""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from pyfmu_scenario.grammar import parse_scenario
from pyfmu_scenario.model import DEFAULT_GUID
from pyfmu_scenario.packaging import package_scenario

pytestmark = pytest.mark.integration

DATA = Path(__file__).resolve().parents[1] / "data"
SCENARIO = parse_scenario((DATA / "scenario.txt").read_text(encoding="utf-8"))


def test_packaging_builds_the_linux64_fmu(tmp_path: Path) -> None:
    build_directory = tmp_path / "build"
    output = tmp_path / "scenario.fmu"

    archive = package_scenario(
        SCENARIO,
        output,
        keep_build_dir=build_directory,
    )

    assert archive == output
    assert (build_directory / "build" / "scenario.so").is_file()

    with zipfile.ZipFile(archive) as bundle:
        names = set(bundle.namelist())
        xml_text = bundle.read("modelDescription.xml").decode("utf-8")

    assert "modelDescription.xml" in names
    assert "binaries/linux64/scenario.so" in names
    assert "binaries/linux64/libscenario.so" not in names

    root = ET.fromstring(xml_text)
    assert root.attrib["modelName"] == "scenario"
    assert root.attrib["guid"] == DEFAULT_GUID
    assert root.find("CoSimulation").attrib["modelIdentifier"] == "scenario"
    variables = [element.attrib["name"] for element in root.iter("ScalarVariable")]
    assert variables == ["scenario_input", *SCENARIO.names]


def test_packaging_keeps_a_custom_guid(tmp_path: Path) -> None:
    guid = "01234567-89ab-cdef-0123-456789abcdef"

    archive = package_scenario(
        SCENARIO,
        tmp_path / "custom.fmu",
        guid=guid,
    )

    with zipfile.ZipFile(archive) as bundle:
        xml_text = bundle.read("modelDescription.xml").decode("utf-8")

    assert f'guid="{guid}"' in xml_text
