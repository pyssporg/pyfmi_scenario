"""Write the SSP parameter set that supplies one scenario.

The set contains the single String parameter ``scenario_input``. It is created
and validated by ``pyssp_standard``; this module writes no XML itself.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_standard import SSV

from .grammar import Scenario, serialize_scenario
from .model import PARAMETER_NAME


def write_parameter_set(
    path: str | Path,
    scenario: Scenario | str,
    *,
    name: str | None = None,
) -> Path:
    """Write ``scenario_input`` to ``path`` as an SSP 1.0 parameter set.

    ``name`` overrides the document name; the facade otherwise derives it from
    the output file stem.
    """
    text = (
        serialize_scenario(scenario)
        if isinstance(scenario, Scenario)
        else scenario
    )
    destination = Path(path)
    with SSV(destination, mode="w") as parameter_set:
        if name is not None:
            parameter_set.xml.name = name
        parameter_set.add_parameter(
            PARAMETER_NAME,
            text,
            type_name="String",
        )
    return destination


__all__ = ["write_parameter_set"]
