# scenario_fmu

`scenario_fmu` is a small FMI 2.0 Co-Simulation project for turning
time-series scenario data into an FMU.

The natural way to use the project is through its Python package. The Python
API packages the compiled FMU binary, generates parameter sets, and provides a
local runner for quick validation.

The repository has two main parts:

- A C++20 shared library that implements the FMI 2.0 Co-Simulation interface.
- A Python package that packages the library into an `.fmu`, emits `.ssv`
  parameter sets, and runs the FMU locally with FMPy.

This README is the entry point. Task-specific details live in `docs/` so the
project stays easy to navigate.

## What You Can Do

- Build the Scenario FMU shared library.
- Package the library as a valid `.fmu`.
- Author scenario data as compact strings or parameter values.
- Generate SSP parameter sets (`.ssv`) for `scenario_input`.
- Run and inspect the FMU locally with FMPy.

## Quick Start

Prerequisites:

- CMake 3.10 or newer
- Ninja
- A C++20 compiler
- `VCPKG_ROOT` pointing to a working vcpkg checkout
- Python 3.8 or newer if you want packaging or runner tools

Build the shared library once:

```bash
git submodule update --init --recursive
cmake --preset=vcpkg
cmake --build build -j
```

Install the Python package:

```bash
python -m pip install -e ./python
```

Create an FMU from Python:

```python
from scenario_fmu_generator import ScenarioFmuPackager

packager = ScenarioFmuPackager("scenario", "scenario", None)
packager.add_raw("speed;L;0,0;5,10;10,10")
packager.build("build/scenario.fmu")
```

Run the packaged FMU:

```bash
scenario-fmu-run --fmu build/scenario.fmu --stop 10 --step 0.1
```

Results are written to `reference_results/` by default.

Run tests when you need to validate the native build:

```bash
ctest --test-dir build -V
```

## Common Workflows

For the shortest path to a working setup, start here:

- [Getting started](docs/getting-started.md)
- [Python API and tooling](docs/python-tools.md)
- [Scenario data format](docs/scenario-format.md)
- [Development notes](docs/development.md)

## Repository Layout

```text
libs/scenario_fmu/     C++20 FMI 2.0 shared library
python/                Python package and CLI tools
test/                  CTest / GoogleTest test targets
scripts/               Optional container-based helper scripts
containers/            Container definition for reproducible builds
3rdParty/reference_fmu/ Reference FMU submodule
```

## Architecture Summary

The FMU exposes:

- One tunable string parameter: `scenario_input`
- One output per parsed series entry
- FMI 2.0 Co-Simulation entry points implemented in
  `libs/scenario_fmu/src/scenario_fmu_interface.cpp`

At initialization, the FMU parses `scenario_input` into internal series data.
At each `fmi2DoStep`, it advances its internal time and evaluates the configured
series at the current communication point.

## Ease-of-Use Notes

- The built shared library is copied into the Python package automatically after
  each CMake build.
- The Python package is the intended day-to-day interface for creating FMUs and
  related artifacts.
- `scenario-fmu-package` can generate a generic FMU even if no scenario data is
  provided.
- `scenario-fmu-ssv` generates a parameter set for `scenario_input`, which is
  useful when integrating into SSP-based workflows.
- `scenario-fmu-run` provides a quick local smoke test and writes CSV output.

## Optional Container Workflow

If you prefer a reproducible Ubuntu 22.04 + GCC 13 environment:

```bash
./scripts/container_build.sh
```

Open a shell in that environment:

```bash
./scripts/container_shell.sh
```

These scripts use `podman`.
