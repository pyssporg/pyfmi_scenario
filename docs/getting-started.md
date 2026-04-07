# Getting Started

This guide covers the shortest path from clone to using the project through its
Python package.

## 1. Prerequisites

Required for the native build:

- CMake 3.10 or newer
- Ninja
- A C++20-capable compiler
- `VCPKG_ROOT` set to a vcpkg checkout

Required for the Python tools:

- Python 3.8 or newer
- `pip`

The test target depends on GoogleTest through vcpkg.

## 2. Clone And Initialize

```bash
git clone <repo-url>
cd scenario_fmu
git submodule update --init --recursive
```

The `reference_fmu` dependency is a submodule. Do not edit it directly.

## 3. Configure And Build

The repository ships a CMake preset named `vcpkg`:

```bash
cmake --preset=vcpkg
cmake --build build -j
```

What this produces:

- `build/libs/scenario_fmu/scenario.so` on Linux
- A copied binary inside `python/src/scenario_fmu_generator/_binaries/`

## 4. Run Tests

```bash
ctest --test-dir build -V
```

This runs the GoogleTest-based CTest target `scenario_tests`.

## 5. Install The Python Package

For local development:

```bash
python -m pip install -e ./python
```

This gives you:

- The Python API in `scenario_fmu_generator`
- The convenience CLIs:
- `scenario-fmu-package`
- `scenario-fmu-ssv`
- `scenario-fmu-run`

## 6. Create An FMU From Python

This is the recommended start point for usage:

```python
from scenario_fmu_generator import ScenarioFmuPackager

packager = ScenarioFmuPackager("scenario", "scenario", None)
packager.add_raw("speed;L;0,0;5,10;10,10")
packager.build("build/scenario.fmu")
```

You can also build the series explicitly:

```python
from scenario_fmu_generator import ScenarioFmuPackager, Variable

packager = ScenarioFmuPackager("scenario", "scenario", None)
packager.add_variable(Variable("speed", "L", [[0.0, 0.0], [5.0, 10.0]]))
packager.build("build/scenario.fmu")
```

## 7. Package An FMU From The CLI

```bash
scenario-fmu-package --out build/scenario.fmu
```

To package a scenario-specific FMU:

```bash
scenario-fmu-package \
  --out build/scenario.fmu \
  --scenario-data "speed;L;0,0;5,10;10,10
mode;ZOH;0,0;3,1;7,2"
```

## 8. Run The FMU Locally

```bash
scenario-fmu-run \
  --fmu build/scenario.fmu \
  --scenario-input "speed;L;0,0;5,10;10,10" \
  --stop 10 \
  --step 0.1
```

By default the runner writes:

- `reference_results/results.csv`
- `reference_results/results.png` when plotting is available

## 9. Generate An SSP Parameter Set

If you want to supply `scenario_input` through SSP tooling:

```bash
scenario-fmu-ssv \
  --out build/scenario.ssv \
  --scenario-data "speed;L;0,0;5,10;10,10"
```

You can also generate the same artifact from Python:

```python
from scenario_fmu_generator import ParameterSetBuilder

builder = ParameterSetBuilder(name="Default")
builder.add_string("scenario_input", "speed;L;0,0;5,10;10,10")
builder.build("build/scenario.ssv")
```

## Troubleshooting

If `cmake --preset=vcpkg` fails:

- Check that `VCPKG_ROOT` is set.
- Check that Ninja is installed.
- Check that your compiler supports C++20.

If `scenario-fmu-package` cannot find the shared library:

- Rebuild with CMake first.
- Confirm the binary was copied into
  `python/src/scenario_fmu_generator/_binaries/<platform>/`.

If tests fail to configure:

- Confirm vcpkg installed `gtest`.
