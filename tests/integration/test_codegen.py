"""The generated source tree is complete, derived from one reduction, stable."""

from __future__ import annotations

from pathlib import Path

import pytest

from pyfmu_scenario.codegen import (
    MODEL_HOOK_SOURCE,
    data_header_name,
    generate_scenario_sources,
    output_bindings,
)
from pyfmu_scenario.grammar import parse_scenario
from pyfmu_scenario.model import build_reduction

pytestmark = pytest.mark.integration

DATA = Path(__file__).resolve().parents[1] / "data"
SCENARIO = parse_scenario((DATA / "scenario.txt").read_text(encoding="utf-8"))


def _tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_generated_files_exist(tmp_path: Path) -> None:
    sources = generate_scenario_sources(SCENARIO, tmp_path)

    assert sources.stem == "scenario"
    assert sources.runtime.is_file()
    assert sources.hooks.is_file()
    assert sources.model.is_file()
    assert sources.data_header.is_file()
    assert sources.cmake.is_file()
    assert sources.fmi2_directory.is_dir()
    assert {path.name for path in sources.headers} == {
        "scenario_InterfaceCommon.h",
        "scenario.h",
    }


def test_model_source_is_the_repository_hook(tmp_path: Path) -> None:
    sources = generate_scenario_sources(SCENARIO, tmp_path)

    assert sources.model.read_bytes() == MODEL_HOOK_SOURCE.read_bytes()


def test_data_table_matches_the_reduction(tmp_path: Path) -> None:
    sources = generate_scenario_sources(SCENARIO, tmp_path)
    text = sources.data_header.read_text(encoding="utf-8")
    reduction = build_reduction(SCENARIO)
    bindings = output_bindings(reduction)

    for name, _value_reference, member in bindings:
        assert f'{{"{name}", {member}}}' in text
        assert member.startswith("SCENARIO_VR_")
    assert f"enum {{ scenario_output_count = {len(bindings)} }};" in text


def test_regeneration_is_byte_identical(tmp_path: Path) -> None:
    first = generate_scenario_sources(SCENARIO, tmp_path / "first")
    second = generate_scenario_sources(SCENARIO, tmp_path / "second")

    assert _tree(first.directory) == _tree(second.directory)


def test_data_header_name_uses_the_generated_stem() -> None:
    assert data_header_name("scenario") == "scenario_scenario_data.h"
