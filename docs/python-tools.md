# Python API And Tooling

The `python/` package is the primary interface for using this project. It wraps
the built shared library and exposes both a small Python API and three command
line tools.

Install it locally with:

```bash
python -m pip install -e ./python
```

## Recommended Python API

The package exports these main types:

- `ScenarioFmuPackager`
- `ParameterSetBuilder`
- `Variable`
- `Variables`

### Build An FMU

```python
from scenario_fmu_generator import ScenarioFmuPackager

packager = ScenarioFmuPackager("scenario", "scenario", None)
packager.add_raw("speed;L;0,0;5,10;10,10")
packager.build("build/scenario.fmu")
```

### Build An FMU From Explicit Variables

```python
from scenario_fmu_generator import ScenarioFmuPackager, Variable

packager = ScenarioFmuPackager("scenario", "scenario", None)
packager.add_variable(Variable("speed", "L", [[0.0, 0.0], [5.0, 10.0]]))
packager.add_variable(Variable("mode", "ZOH", [[0.0, 0.0], [3.0, 1.0]]))
packager.build("build/scenario.fmu")
```

### Generate An SSV Parameter Set

```python
from scenario_fmu_generator import ParameterSetBuilder

builder = ParameterSetBuilder(name="Default")
builder.add_string("scenario_input", "speed;L;0,0;5,10;10,10")
builder.build("build/scenario.ssv")
```

### Notes

- `ScenarioFmuPackager` expects the shared library to already exist in the
  package `_binaries/<platform>/` directory.
- That binary is populated by the CMake build.
- `add_raw()` is the fastest path when your scenario already exists as a string.
- `Variable` is the better fit when another Python system generates the series.

## CLI Commands

### `scenario-fmu-package`

Packages the built Scenario FMU shared library into a valid FMI 2.0
Co-Simulation `.fmu`.

Example:

```bash
scenario-fmu-package --out build/scenario.fmu
```

Useful options:

- `--out`: Output `.fmu` path
- `--model-id`: FMI `modelIdentifier` and binary base name
- `--model-name`: Human-readable `modelName`
- `--guid`: Explicit FMU GUID
- `--scenario-data`: Inline scenario string

Behavior:

- Reads the platform-specific shared library from `_binaries/<platform>/`
- Generates `modelDescription.xml`
- Creates an `.fmu` zip with `modelDescription.xml` and `binaries/...`

If `--scenario-data` is omitted, the packager emits a generic FMU with default
outputs.

### `scenario-fmu-ssv`

Generates an SSP parameter set (`.ssv`) containing the `scenario_input` string.

Example:

```bash
scenario-fmu-ssv \
  --name Default \
  --out build/scenario.ssv \
  --scenario-data "speed;L;0,0;5,10;10,10"
```

Useful options:

- `--name`: Parameter set name
- `--out`: Output `.ssv` path
- `--scenario-data`: Value assigned to `scenario_input`

### `scenario-fmu-run`

Runs an `.fmu` locally with FMPy, writes CSV output, and optionally creates a
plot.

Example:

```bash
scenario-fmu-run \
  --fmu build/scenario.fmu \
  --scenario-input "speed;L;0,0;5,10;10,10" \
  --start 0 \
  --stop 10 \
  --step 0.1
```

Useful options:

- `--fmu`: Path to the `.fmu`
- `--scenario-input`: Runtime value for `scenario_input`
- `--start`: Start time
- `--stop`: Stop time
- `--step`: Communication step size
- `--out-dir`: Output directory for CSV and plot

Outputs:

- `results.csv`
- `results.png` when `matplotlib` is available

## Packaging Notes

The CMake build copies the compiled library into the Python package here:

```text
python/src/scenario_fmu_generator/_binaries/<platform>/
```

That means the normal sequence is:

1. Build with CMake.
2. Install the Python package.
3. Use the Python API or run `scenario-fmu-package`.

## Building Python Distributions

To build a wheel or source distribution:

```bash
cd python
python -m build
```

The package metadata lives in `python/pyproject.toml`.
