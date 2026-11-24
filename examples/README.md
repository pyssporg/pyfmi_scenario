# pyfmi_scenario examples

Four runnable paths from scenario text (or a `Scenario` in Python) to a packaged
FMI 2.0 Co-Simulation FMU.

## Run

From the workspace root:

```bash
bash repos/pyfmi_scenario/examples/01-cli-quickstart/run.sh
```

The headline example: `scenario.txt` declares a linear ramp (`L`), a
zero-order-hold gear (`ZOH`), and a nearest-neighbour mode (`NN`); the script
packages the FMU, writes the SSV parameter set, and simulates the FMU with
FMPy.

| Output | Contents |
| --- | --- |
| `build/examples/01-cli-quickstart/scenario.fmu` | the packaged FMU |
| `build/examples/01-cli-quickstart/scenario.ssv` | `scenario_input` as an SSP 1.0 parameter set |
| `build/examples/01-cli-quickstart/results.csv` | the FMPy simulation result |

```text
build/examples/01-cli-quickstart/scenario.fmu
build/examples/01-cli-quickstart/scenario.ssv
build/examples/01-cli-quickstart/results.csv
```

The script accepts one optional `--out DIR`. The CLI calls it makes, one by
one, are `pyfmi-scenario package`, `pyfmi-scenario ssv`, and `pyfmi-scenario
run`.

### Python API

Builds `Sample`/`Series`/`Scenario` in code and packages the FMU with a custom
GUID:

```bash
python repos/pyfmi_scenario/examples/02-python-api/run.py
```

```text
build/examples/02-python-api/scenario.fmu
```

### Parameter set

Parses `examples/01-cli-quickstart/scenario.txt` and writes the
`scenario_input` binding as an SSP 1.0 parameter set named `ScenarioSet`:

```bash
python repos/pyfmi_scenario/examples/03-parameter-set/run.py
```

```text
build/examples/03-parameter-set/scenario.ssv
```

### Simulate

Packages a scenario and drives it with `fmpy.simulate_fmu`, passing the text
through `scenario_input` (`start_values`) and selecting the series as outputs:

```bash
python repos/pyfmi_scenario/examples/04-simulate/run.py
```

```text
build/examples/04-simulate/scenario.fmu
build/examples/04-simulate/results.csv
```

## Setup

Use the workspace virtualenv and an editable install; no `PYTHONPATH` is
needed:

```bash
source .venv/bin/activate  # the workspace venv, see the workspace README.md
pip install -e repos/pyfmi_scenario
pip install fmpy
```

Packaging an `.fmu` compiles the generated FMI runtime, so `cmake` and `g++`
must be on `PATH`. Every example accepts one optional `--out DIR`; the default
is the gitignored `build/examples/<name>/`.

## Notes

- Outputs go only under the chosen `--out` directory (`build/` is gitignored).
- `C` (cubic) is declared by the grammar but unsupported: `parse_scenario`,
  `Series`, and the CLI all reject it. Use `L`, `ZOH`, or `NN`.
