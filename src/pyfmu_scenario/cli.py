"""Command line for pyfmu_scenario.

The commands are deliberately thin: parsing, packaging, and SSP writing live
in the library modules; this module only binds arguments to them.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from .model import DEFAULT_GUID, MODEL_IDENTIFIER
from .packaging import load_scenario, package_scenario
from .parameter_set import write_parameter_set


def _add_scenario_source(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--scenario",
        type=Path,
        metavar="PATH",
        help="Scenario text file.",
    )
    group.add_argument(
        "--scenario-text",
        metavar="TEXT",
        help="Scenario grammar text passed on the command line.",
    )


def _configure_package(parser: argparse.ArgumentParser) -> None:
    _add_scenario_source(parser)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        metavar="FMU",
        help="Output .fmu archive.",
    )
    parser.add_argument(
        "--guid",
        default=DEFAULT_GUID,
        metavar="GUID",
        help=f"FMU GUID (default: {DEFAULT_GUID}).",
    )
    parser.add_argument(
        "--model-id",
        default=MODEL_IDENTIFIER,
        metavar="NAME",
        help="Must be 'scenario'; the generated identity is fixed.",
    )
    parser.add_argument(
        "--keep-build-dir",
        type=Path,
        default=None,
        metavar="DIR",
        help="Retain generated sources and the CMake build in DIR.",
    )


def _configure_ssv(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--scenario",
        type=Path,
        required=True,
        metavar="PATH",
        help="Scenario text file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        metavar="SSV",
        help="Output .ssv parameter set.",
    )
    parser.add_argument(
        "--parameter-set-name",
        default="ScenarioSet",
        metavar="NAME",
        help="Parameter-set document name (default: ScenarioSet).",
    )


def _configure_run(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--fmu",
        type=Path,
        required=True,
        metavar="PATH",
        help="Scenario FMU to simulate.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        metavar="CSV",
        help="Write the simulation result to CSV.",
    )


def _package(args: argparse.Namespace) -> int:
    source = args.scenario if args.scenario is not None else args.scenario_text
    archive = package_scenario(
        source,
        args.output,
        guid=args.guid,
        model_id=args.model_id,
        keep_build_dir=args.keep_build_dir,
    )
    print(archive)
    return 0


def _ssv(args: argparse.Namespace) -> int:
    scenario = load_scenario(args.scenario)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    path = write_parameter_set(
        args.output,
        scenario,
        name=args.parameter_set_name,
    )
    print(path)
    return 0


def _run_fmu(fmu: Path, output: Path | None) -> int:
    try:
        import fmpy
    except ImportError as exc:
        raise RuntimeError(
            "the 'run' command requires fmpy; install the dev extra with "
            "`pip install 'pyfmu-scenario[dev]'`"
        ) from exc

    description = fmpy.read_model_description(str(fmu))
    names = [
        variable.name
        for variable in description.modelVariables
        if variable.causality == "output"
    ]
    if not names:
        names = [variable.name for variable in description.modelVariables]

    experiment = description.defaultExperiment
    start = (
        experiment.startTime
        if experiment is not None and experiment.startTime is not None
        else 0.0
    )
    stop = (
        experiment.stopTime
        if experiment is not None and experiment.stopTime is not None
        else 10.0
    )

    start_values = {
        variable.name: variable.start
        for variable in description.modelVariables
        if variable.causality == "parameter" and variable.start is not None
    }

    result = fmpy.simulate_fmu(
        str(fmu),
        start_time=start,
        stop_time=stop,
        output=names,
        start_values=start_values,
    )

    if output is None:
        print(f"{fmu}: {len(result)} samples")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(result.dtype.names)
        for row in result:
            writer.writerow([row[name] for name in result.dtype.names])
    print(output)
    return 0


def _run(args: argparse.Namespace) -> int:
    return _run_fmu(args.fmu, args.output)


def main(argv: list[str] | None = None) -> int:
    """Run the command line; return 0 on success and 1 on failure."""
    parser = argparse.ArgumentParser(
        prog="pyfmu-scenario",
        description="Build scenario-series FMUs, parameter sets, and runs.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    package = commands.add_parser(
        "package",
        help="Build and package an FMI 2.0 Co-Simulation FMU.",
    )
    _configure_package(package)
    package.set_defaults(handler=_package)

    ssv = commands.add_parser(
        "ssv",
        help="Write the scenario_input parameter set.",
    )
    _configure_ssv(ssv)
    ssv.set_defaults(handler=_ssv)

    run = commands.add_parser(
        "run",
        help="Simulate a scenario FMU with fmpy.",
    )
    _configure_run(run)
    run.set_defaults(handler=_run)

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # Argument errors are failures; --help and --version stay successful.
        return 0 if exc.code == 0 else 1

    try:
        return args.handler(args)
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"pyfmu-scenario: {exc}", file=sys.stderr)
        return 1


__all__ = ["main"]
