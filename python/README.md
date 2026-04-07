# scenario-fmu-generator

Python tooling for packaging and running the Scenario FMU.

This package is the user-facing layer on top of the C++ FMU implementation in
the repository root. It provides a small Python API plus CLIs to:

- package the built shared library into an `.fmu`
- generate an `.ssv` parameter set for `scenario_input`
- run the FMU locally with FMPy

For the main project overview and build instructions, start at the repository
root `README.md`.

## Install

Published package:

```bash
pip install scenario-fmu-generator
```

Local development install:

```bash
python -m pip install -e ./python
```

## Recommended Usage

The Python API is the intended start point.

Create an FMU:

```python
from scenario_fmu_generator import ScenarioFmuPackager

packager = ScenarioFmuPackager("scenario", "scenario", None)
packager.add_raw("var1;L;1,0;3,0.5;5,4;9,2")
packager.build("build/scenario.fmu")
```

Generate an SSP parameter set:

```python
from scenario_fmu_generator import ParameterSetBuilder

builder = ParameterSetBuilder(name="Default")
builder.add_string("scenario_input", "var1;L;1,0;3,0.5;5,4;9,2")
builder.build("build/scenario.ssv")
```

## Commands

### Package An FMU

```bash
scenario-fmu-package --out build/scenario.fmu
```

With scenario data:

```bash
scenario-fmu-package --out build/scenario.fmu --scenario-data "var1;L;1,0;3,0.5;5,4;9,2
var2;ZOH;2,0;3,0.5;5,4;9,2
var3;NN;0,0;1,0.5;2,4;3,2"
```

### Generate An SSV Parameter Set

```bash
scenario-fmu-ssv --out build/scenario.ssv --scenario-data "var1;L;1,2;3,0.5;4,3;7,2
var2;ZOH;2,2;3,0.5;5,5;9,2
var3;NN;0,0;1,0.5;2,4;3,2"
```

### Run An FMU

```bash
scenario-fmu-run --fmu build/scenario.fmu --stop 10 --step 0.1
```

## Build Python Distributions

```bash
cd python
python -m build
```

## Notes

- The CMake build copies the compiled shared library into
  `src/scenario_fmu_generator/_binaries/<platform>/`.
- `scenario-fmu-package` depends on that copied binary being present.
- For the full CLI and scenario format reference, see `../docs/python-tools.md`
  and `../docs/scenario-format.md`.
