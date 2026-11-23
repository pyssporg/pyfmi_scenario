# pyfmu_scenario examples

Four small, runnable examples. Each writes only to its own `out/` directory,
which is gitignored.

## Prerequisites

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

- `cmake` and `g++` are required by every example that packages an `.fmu`
  (01, 02, 04).
- 04 uses `fmpy` and writes `outputs.png` only when `matplotlib` is available.
- Examples 02-04 add `src/` to `sys.path`, so they also run from a source
  checkout without an editable install. 01 falls back to
  `python -m pyfmu_scenario` when the `pyfmu-scenario` console script is absent.

## 01 - CLI quickstart

`scenario.txt` has three series: a linear ramp (`L`), a zero-order-hold gear
(`ZOH`), and a nearest-neighbour mode (`NN`). `run.sh` packages the FMU, writes
the SSV, and simulates it with FMPy:

```bash
bash examples/01-cli-quickstart/run.sh
```

Outputs: `out/scenario.fmu`, `out/scenario.ssv`, `out/results.csv`.

The CLI equivalents, one by one:

```bash
pyfmu-scenario package --scenario examples/01-cli-quickstart/scenario.txt \
  --output examples/01-cli-quickstart/out/scenario.fmu
pyfmu-scenario ssv --scenario examples/01-cli-quickstart/scenario.txt \
  --output examples/01-cli-quickstart/out/scenario.ssv
pyfmu-scenario run --fmu examples/01-cli-quickstart/out/scenario.fmu \
  --output examples/01-cli-quickstart/out/results.csv
```

## 02 - Python API

Builds `Sample`/`Series`/`Scenario` in code, round-trips the canonical text,
packages with a custom GUID, and reads the `.fmu` back with `zipfile`:

```bash
python examples/02-python-api/run.py
```

Output: `out/scenario.fmu`, plus the model name, GUID, variables, and archive
entries printed to the terminal.

## 03 - Parameter set

Parses `examples/01-cli-quickstart/scenario.txt` and writes the `scenario_input`
binding as an SSP 1.0 parameter set named `ScenarioSet`:

```bash
python examples/03-parameter-set/run.py
```

Output: `out/scenario.ssv`; the script prints the root element, namespace, and
binding.

## 04 - Simulate

Packages a scenario and drives it with `fmpy.simulate_fmu`, passing the text
through `scenario_input` (`start_values`) and selecting the series as outputs:

```bash
python examples/04-simulate/run.py
```

Outputs: `out/scenario.fmu`, `out/results.csv`, and `out/outputs.png` when
`matplotlib` is installed. If `fmpy` is missing the script exits with an install
hint instead of faking a run.

## Notes

- Outputs are written only under each example's `out/`; `out/` is gitignored.
- `C` (cubic) is declared by the grammar but unsupported: `parse_scenario`,
  `Series`, and the CLI all reject it. Use `L`, `ZOH`, or `NN`.
