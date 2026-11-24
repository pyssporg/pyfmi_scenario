# pyfmu_scenario

`pyfmu_scenario` turns scenario time-series text into one packaged FMI 2.0
Co-Simulation FMU. The FMU exposes a single String parameter,
`scenario_input`, and one Real output per named series. The scenario data
travels inside the FMU, so an importing tool reads the outputs without a
custom data loader.

## What it is not

- It is an FMU producer, not a SysML parser.
- It emits no SSD, SSV, SSM, or SSP. The `ssv` helper writes one parameter set
  for `scenario_input`; it does not reinterpret the series as SSP parameters.
- It does not assemble systems. `pyssp_sysml` consumes the packaged FMU.
- It does not target FMI 3.0 or Model Exchange.

## Install

Python 3.11 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

The runtime dependencies are not PyPI releases:
`experimental_pyssp_standard` is a direct-URL wheel from its GitHub release,
and `pyfmi-interfaces` comes from its own release assets. Do not install a PyPI
`pyssp_standard` release into the same environment; it supplies the same
import package as `experimental_pyssp_standard`.

`cmake` and `g++` are needed only when packaging an FMU. The Python wheel is
pure Python.

## Quickstart

Write a scenario file, `scenario.txt`:

```text
Alt;L;0.0,0.0;300.0,10000.0
Mach;L;0.0,0.0;300.0,1.2
heat_load;ZOH;0.0,50.0;150.0,4000.0
```

Package it as an FMU, generate a matching parameter set, and run it:

```bash
pyfmu-scenario package --scenario scenario.txt --output scenario.fmu
pyfmu-scenario ssv --scenario scenario.txt --output scenario.ssv
pyfmu-scenario run --fmu scenario.fmu --output results.csv
```

`package` also accepts `--scenario-text` for an inline scenario and `--guid` to
override the default GUID. `run` simulates the model's default experiment with
FMPy and writes a CSV when `--output` is given. Each subcommand accepts
`--help`. The format, interpolation semantics, error types, and FMU mapping are
in [docs/scenario-format.md](docs/scenario-format.md).

## Examples

Runnable examples live in [examples/](examples/README.md): CLI quickstart, the
Python API, the SSV parameter set, and a FMPy simulation.

```bash
bash examples/01-cli-quickstart/run.sh
```

## Architecture and boundary

The producer is one direction:

```text
scenario text -> parse_scenario -> Scenario -> build_reduction
              -> pyfmi_interfaces reduction
              -> modelDescription.xml, C/C++ runtime, .fmu archive
```

- `pyfmi_interfaces` owns the FMI plumbing: `modelDescription.xml`
  serialization, C headers, C++ Co-Simulation entry points, FMI headers, and
  the `.fmu` zip.
- `pyssp_standard` owns the FMI 2.0 XML objects and the archive and
  parameter-set facades.
- This repository owns the scenario grammar, the reference evaluator, the five
  model hooks, and the CMake build.

No FMI XML, `.fmu` packaging, or FMI runtime is hand-rolled here.

## Requirements and limits

- FMI 2.0 Co-Simulation only; linux64 is the first supported platform.
- Scenario data must arrive through the String parameter. The generated
  runtime cannot use a resource location.
- `L`, `ZOH`, and `NN` interpolation are implemented. `C` is declared by the
  grammar and rejected as unsupported.
- Packaging needs `cmake` and `g++`; installing the Python package does not.
- Identity is fixed: model name and identifier are `scenario`, the generation
  tool is `pyfmu-scenario`, and the default GUID is
  `9524b75e-dc71-47cd-a02f-e22b95a3f76d`. `build_reduction(..., guid=...)`
  overrides it.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

python -m pytest
ruff check src tests examples
```

`python -m pytest` is the CI test selection; `cmake` and `g++` are needed only
when a test or an example packages an FMU. Contributor rules and layout are in
[AGENTS.md](AGENTS.md).

## Documentation

- [Scenario data format](docs/scenario-format.md)
- [Intent](docs/breakdown/00-intent/intent.md)
- [Product breakdown](docs/breakdown/)
- [Contributor rules](AGENTS.md)
- [Changelog](CHANGELOG.md)

## License

MIT, © 2024 Linköping University.
