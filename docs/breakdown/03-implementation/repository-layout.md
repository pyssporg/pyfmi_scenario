---
id: INFO-006
type: info
title: Repository layout
summary: Python package, tests, native runtime, and their build entry points
date: 2026-11-23
status: current
---

# Repository layout

The repository separates the Python producer, its tests, and the native runtime build.

- **`src/pyfmu_scenario/`:** the import package; grammar, reference evaluator, interface model, modelDescription writer, parameter-set writer, code generation, packaging, and the console entry point.
- **`src/runtime/scenario_model.cpp`:** the hand-written model that implements the five runtime hooks copied over the generated stub.
- **`tests/`:** the pytest suite, with fixtures and the baseline CSV under `tests/data/`.
- **Generated build directory:** `codegen` writes the generated FMI sources, the data table, and a `CMakeLists.txt`; `package` compiles the FMI 2.0 Co-Simulation runtime there. There is no checked-in top-level `CMakeLists.txt`.
- **`pyproject.toml`:** PEP 621 metadata, the `pyfmu-scenario` console script, and the dev dependencies.
- **`docs/`:** the scenario-format reference and the product breakdown in `docs/breakdown/`.
- **`.github/workflows/`:** the `tests` and `wheels` CI pair.
