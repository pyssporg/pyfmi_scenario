"""Generate the C++ runtime sources and build script for one scenario FMU.

The FMI entry points, headers, and value-reference enum are owned by
``pyfmi_interfaces``. This module only orchestrates those generators, replaces
the generated model stub with the repository's scenario hook, and adds the two
artifacts the runtime needs beyond the generic component layout:

- ``<stem>_scenario_data.h``, the output-name to value-reference table;
- ``CMakeLists.txt``, which builds ``scenario.so`` from the generated runtime
  and the scenario model.

Everything is derived from the single :class:`Reduction`, so the data table
cannot drift from the value-reference mapping in the generated header.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from pyfmi_interfaces.c.headers import (
    generate_c_headers,
    header_stem,
)
from pyfmi_interfaces.c.runtime import (
    generate_c_runtime,
    hooks_header_name,
    model_source_name,
    runtime_source_name,
)
from pyfmi_interfaces.core import (
    Component,
    Reduction,
    sanitize_identifier,
)

from .grammar import Scenario
from .model import build_reduction

#: Prefix the generated C symbols and file names are built from.
PREFIX = "scenario"

#: The hand-written model hook copied over the generated stub. It travels in
#: the wheel as package data, so an installed package can package an FMU.
MODEL_HOOK_SOURCE = Path(__file__).resolve().parent / "_runtime" / "scenario_model.cpp"


@dataclass(frozen=True)
class ScenarioSources:
    """The generated source tree, with every path a build needs."""

    directory: Path
    stem: str
    headers: tuple[Path, ...]
    runtime: Path
    hooks: Path
    model: Path
    data_header: Path
    cmake: Path

    @property
    def fmi2_directory(self) -> Path:
        return self.directory / "fmi2"


def _component(reduction: Reduction) -> Component:
    components = list(reduction.components)
    if len(components) != 1:
        raise ValueError(
            "the scenario generator expects exactly one exported component, "
            f"got {len(components)}"
        )
    return components[0]


def scenario_stem(reduction: Reduction) -> str:
    """The generated stem, ``scenario`` for the direct scenario FMU."""
    component = _component(reduction)
    return header_stem(
        PREFIX, component.name, direct=reduction.identity.direct
    )


def data_header_name(stem: str) -> str:
    """File name of the output binding table."""
    return f"{stem}_scenario_data.h"


def _c_string(text: str) -> str:
    """A double-quoted C string literal for ``text``."""
    escaped: list[str] = []
    for character in text:
        if character == "\\":
            escaped.append("\\\\")
        elif character == '"':
            escaped.append('\\"')
        elif character == "\n":
            escaped.append("\\n")
        elif character == "\r":
            escaped.append("\\r")
        elif character == "\t":
            escaped.append("\\t")
        elif character.isprintable():
            escaped.append(character)
        else:
            escaped.append(f"\\x{ord(character):02x}")
    return '"' + "".join(escaped) + '"'


def output_bindings(reduction: Reduction) -> tuple[tuple[str, int, str], ...]:
    """``(fmi name, value reference, enum member)`` for every declared output."""
    component = _component(reduction)
    upper = sanitize_identifier(scenario_stem(reduction))
    bindings = []
    for variable in component.variables:
        if variable.causality != "output":
            continue
        member = f"{upper}_VR_" + sanitize_identifier(variable.c_name)
        bindings.append((variable.name, variable.value_reference, member))
    if not bindings:
        raise ValueError("the scenario reduction has no output variables")
    return tuple(bindings)


def data_header_text(reduction: Reduction) -> str:
    """Text of ``<stem>_scenario_data.h``.

    The table is the runtime's declaration of which series must be present in
    ``scenario_input``; it is built from the same ``Reduction`` as the
    generated value-reference enum.
    """
    stem = scenario_stem(reduction)
    guard = f"{sanitize_identifier(stem)}_SCENARIO_DATA_H"
    bindings = output_bindings(reduction)
    lines = [
        f"#ifndef {guard}",
        f"#define {guard}",
        "",
        '#include "fmi2/fmi2TypesPlatform.h"',
        '#include "' + f"{stem}.h" + '"',
        "",
        "/* Generated from the scenario interface. Do not edit manually. */",
        "",
        f"typedef struct {stem}_OutputBinding {{",
        "  const char* name;",
        "  fmi2ValueReference vr;",
        f"}} {stem}_OutputBinding;",
        "",
        f"static const {stem}_OutputBinding {stem}_outputs[] = {{",
    ]
    for name, value_reference, member in bindings:
        lines.append(f"  {{{_c_string(name)}, {member}}},")
    lines.extend(
        [
            "};",
            "",
            f"enum {{ {stem}_output_count = {len(bindings)} }};",
            "",
            f"#endif  /* {guard} */",
            "",
        ]
    )
    return "\n".join(lines)


def cmake_text(stem: str) -> str:
    """Text of the build-directory ``CMakeLists.txt``.

    The shared library is named exactly the modelIdentifier: ``PREFIX ""``
    removes the platform ``lib`` prefix, so the archive entry is
    ``binaries/linux64/<stem>.so``.
    """
    return "\n".join(
        [
            "cmake_minimum_required(VERSION 3.16)",
            "project(scenario_runtime LANGUAGES CXX)",
            "",
            f"add_library({stem} SHARED",
            f'  "${{CMAKE_CURRENT_SOURCE_DIR}}/{stem}_fmi.cpp"',
            f'  "${{CMAKE_CURRENT_SOURCE_DIR}}/{stem}_model.cpp"',
            ")",
            "",
            f"set_target_properties({stem} PROPERTIES",
            "  CXX_STANDARD 17",
            "  CXX_STANDARD_REQUIRED ON",
            "  CXX_EXTENSIONS OFF",
            '  PREFIX ""',
            f'  OUTPUT_NAME "{stem}"',
            ")",
            "",
            f"target_include_directories({stem} PRIVATE",
            '  "${CMAKE_CURRENT_SOURCE_DIR}"',
            '  "${CMAKE_CURRENT_SOURCE_DIR}/fmi2"',
            ")",
            "",
        ]
    )


def generate_scenario_sources(
    scenario: Scenario,
    output_dir: str | Path,
    *,
    guid: str | None = None,
) -> ScenarioSources:
    """Write the complete C++ source tree for ``scenario`` into ``output_dir``.

    The ``Reduction`` is built once, then both ``pyfmi_interfaces`` generators
    run from it. ``<stem>_model.cpp`` is replaced unconditionally with the
    repository hook, because the generator only creates that file when it is
    absent.
    """
    reduction = (
        build_reduction(scenario, guid=guid)
        if guid is not None
        else build_reduction(scenario)
    )
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    headers = tuple(
        generate_c_headers(reduction, directory, prefix=PREFIX)
    )
    generate_c_runtime(reduction, directory, prefix=PREFIX)

    stem = scenario_stem(reduction)
    runtime_path = directory / runtime_source_name(stem)
    hooks_path = directory / hooks_header_name(stem)
    model_path = directory / model_source_name(stem)
    if not MODEL_HOOK_SOURCE.is_file():
        raise FileNotFoundError(
            f"scenario model hook not found: {MODEL_HOOK_SOURCE}"
        )
    shutil.copyfile(MODEL_HOOK_SOURCE, model_path)

    data_path = directory / data_header_name(stem)
    data_path.write_text(data_header_text(reduction), encoding="utf-8")

    cmake_path = directory / "CMakeLists.txt"
    cmake_path.write_text(cmake_text(stem), encoding="utf-8")

    missing = [
        path
        for path in (runtime_path, hooks_path, model_path)
        if not path.is_file()
    ]
    if missing:
        raise RuntimeError(
            "the C runtime generator did not write "
            + ", ".join(str(path) for path in missing)
        )

    return ScenarioSources(
        directory=directory,
        stem=stem,
        headers=headers,
        runtime=runtime_path,
        hooks=hooks_path,
        model=model_path,
        data_header=data_path,
        cmake=cmake_path,
    )


__all__ = [
    "MODEL_HOOK_SOURCE",
    "PREFIX",
    "ScenarioSources",
    "cmake_text",
    "data_header_name",
    "data_header_text",
    "generate_scenario_sources",
    "output_bindings",
    "scenario_stem",
]
