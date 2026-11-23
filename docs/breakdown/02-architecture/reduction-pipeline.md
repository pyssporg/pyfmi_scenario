---
id: INFO-004
type: info
title: Reduction pipeline
summary: Scenario text becomes one interface model, then FMI 2.0 artifacts
date: 2026-11-23
status: current
---

# Reduction pipeline

The scenario text becomes one `pyfmi_interfaces` reduction, and every FMI artifact is generated from that reduction.

- **Parse:** `parse_scenario` turns the `scenario_input` text into typed `Scenario` and `Series` objects.
- **Canonicalize:** `serialize_scenario` produces the round-trippable text used as the parameter start value.
- **Reduce:** `build_reduction` maps the scenario onto a direct-FMU `Reduction` with one component and fixed identity.
- **Variables:** value reference `0` is `scenario_input`; outputs are `1..N` in declaration order.
- **Serialize:** `build_model_description` writes the FMI 2.0 document through `pyssp_standard` and the `pyfmi_interfaces` codec.
- **Complete:** the C++ runtime, the five model hooks, the CMake build, and the `.fmu` archive finish the artifact.
