---
id: INFO-002
type: info
title: Scenario FMU capability
summary: One String parameter, one Real output per series, interpolation inside the FMU
date: 2026-11-23
status: current
---

# Scenario FMU capability

`pyfmi_scenario` turns scenario time-series text into one packaged FMI 2.0 Co-Simulation FMU.

- **Single input:** one String parameter, `scenario_input`, whose value is the canonical serialized scenario text.
- **Outputs:** one Real output per declared series, named exactly after the series, in declaration order.
- **Interpolation:** `L`, `ZOH`, and `NN` are evaluated inside the FMU; `C` is rejected as unsupported.
- **Self-contained data:** the scenario travels inside the FMU, so an importing tool reads outputs without custom data handling.
- **Fixed identity:** model name and identifier are `scenario`, and the default GUID is fixed.
- **Platform:** linux64 is the first supported target; the runtime is built when the FMU is packaged.
- **Grammar:** the text format and its evaluation rules are documented in `docs/scenario-format.md`.
