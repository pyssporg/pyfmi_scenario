---
id: INFO-008
type: info
title: Test strategy
summary: Unit grammar and interface checks, FMPy end-to-end, golden CSV oracle
date: 2026-11-23
status: current
---

# Test strategy

Each claim about the scenario producer has a test level that can fail independently.

- **Unit:** grammar errors, canonical serialization, interpolation semantics, value references, XML attributes, and the SSV binding.
- **Integration:** the generated source tree is complete, derived from one reduction, and byte-identical on regeneration.
- **Contract:** the generated `modelDescription.xml` is compared with the reference scenario FMU, allowing only the `author` and `generationTool` rename.
- **End to end:** FMPy loads a packaged `.fmu`, steps it, and its outputs are compared with the Python evaluator.
- **Oracle:** the reference evaluator in `src/pyfmi_scenario/series.py` is the semantic source for the generated runtime.
- **CI:** the tests workflow runs lint and the pytest suite on Python 3.11 and 3.12 with `cmake` and `g++` available.
- **Skips:** checks that need a missing toolchain, FMPy, or the `ssp_references` fixture skip with a reason.
