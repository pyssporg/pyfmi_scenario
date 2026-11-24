---
id: INFO-011
type: info
title: Command line
summary: The pyfmi-scenario console script with package, ssv, and run
date: 2026-11-23
status: current
---

# Command line

The `pyfmi-scenario` console script exposes the three producer operations.

- **`package`:** takes `--scenario PATH` or `--scenario-text TEXT`, writes `--output FMU`, and accepts `--guid`, `--model-id`, and `--keep-build-dir`.
- **`ssv`:** takes `--scenario`, `--output SSV`, and an optional `--parameter-set-name`.
- **`run`:** takes `--fmu` and an optional `--output CSV`; it simulates with `fmpy` over the model's default experiment.
- **Model id:** `--model-id` must be `scenario`; any other value is refused.
- **Help:** `pyfmi-scenario --help` and `pyfmi-scenario <command> --help` list the accepted arguments.
- **Implementation:** `src/pyfmi_scenario/cli.py` binds the commands to the parser, packaging, parameter-set writer, and FMPy runner.
