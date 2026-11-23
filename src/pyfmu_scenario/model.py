"""Map a parsed scenario onto the ``pyfmi_interfaces`` interface model.

Value reference ``0`` is the String parameter ``scenario_input`` and carries the
canonical scenario text as its start value in the FMI document. Outputs are
numbered ``1..N`` in declaration order, and their 1-based XML indices are
``2..N+1`` because the parameter occupies index ``1``.

The same reduction also drives the C header, so it needs storage for every
value reference: the parameter is a declared member and each output is the
``value`` field of a single-Real port payload. The generated C member for an
output is therefore ``<port>.value`` while its FMI name stays the series name.
"""

from __future__ import annotations

from dataclasses import replace

from pyfmi_interfaces import (
    Component,
    Experiment,
    ExportIdentity,
    Reduction,
    Variable,
)
from pyfmi_interfaces.core import Field, PortGroup

from . import __version__
from .grammar import Scenario, serialize_scenario

MODEL_NAME = "scenario"
MODEL_IDENTIFIER = "scenario"
PARAMETER_NAME = "scenario_input"
DEFAULT_GUID = "9524b75e-dc71-47cd-a02f-e22b95a3f76d"
GENERATION_TOOL = "pyfmu-scenario"
AUTHOR = "pyssporg"
VERSION = __version__
DEFAULT_EXPERIMENT = Experiment(
    start_time=0.0,
    stop_time=10.0,
    tolerance=0.0001,
)


def build_variables(
    scenario: Scenario,
    *,
    parameter_start: str | None = None,
) -> tuple[Variable, ...]:
    """The parameter and output variables in declaration order."""
    start = (
        serialize_scenario(scenario)
        if parameter_start is None
        else parameter_start
    )
    variables = [
        Variable(
            name=PARAMETER_NAME,
            type_name="String",
            causality="parameter",
            variability="tunable",
            value_reference=0,
            index=1,
            description=None,
            member=PARAMETER_NAME,
            start=start,
            start_text=start,
        )
    ]
    for value_reference, series in enumerate(scenario.series, start=1):
        variables.append(
            Variable(
                name=series.name,
                type_name="Real",
                causality="output",
                variability=None,
                value_reference=value_reference,
                index=value_reference + 1,
                description=None,
                # The C header stores an output inside its payload struct, so
                # the value reference points at ``<port>.value``.
                member=f"{series.name}.value",
            )
        )
    return tuple(variables)


def build_ports(scenario: Scenario) -> tuple[PortGroup, ...]:
    """One output payload per series, giving the C runtime its storage.

    The generated component header declares a struct member per port and maps
    each output value reference to ``&instance-><port>.value``. The port
    definition is shared because every scenario output is a single Real.
    """
    return tuple(
        PortGroup(
            name=series.name,
            definition="ScenarioOutput",
            direction="out",
            causality="output",
            fields=(Field("value", "Real"),),
            doc=None,
        )
        for series in scenario.series
    )


def build_component(scenario: Scenario) -> Component:
    """The single exported component for one scenario.

    The parameter keeps no C++ start value: the canonical scenario text spans
    several lines, and the generated C literal escapes quotes but not
    newlines. The authoritative start value is the one written to
    ``modelDescription.xml`` by :mod:`pyfmu_scenario.model_description`; the
    FMI importer sets the parameter before initialization.
    """
    storage = tuple(
        replace(variable, start=None, start_text=None)
        if variable.causality == "parameter"
        else variable
        for variable in build_variables(scenario)
    )
    return Component(
        name=MODEL_IDENTIFIER,
        doc=None,
        parameters=(Field(PARAMETER_NAME, "String"),),
        ports=build_ports(scenario),
        variables=storage,
        attributes=(),
    )


def build_reduction(
    scenario: Scenario,
    *,
    guid: str = DEFAULT_GUID,
) -> Reduction:
    """The complete generator input for one scenario."""
    return Reduction(
        components=(build_component(scenario),),
        identity=ExportIdentity(
            system=MODEL_NAME,
            direct=True,
            guid=guid,
        ),
        package="",
        experiment=DEFAULT_EXPERIMENT,
        root=None,
        attributes=(),
    )


__all__ = [
    "AUTHOR",
    "DEFAULT_EXPERIMENT",
    "DEFAULT_GUID",
    "GENERATION_TOOL",
    "MODEL_IDENTIFIER",
    "MODEL_NAME",
    "PARAMETER_NAME",
    "VERSION",
    "build_component",
    "build_ports",
    "build_reduction",
    "build_variables",
]
