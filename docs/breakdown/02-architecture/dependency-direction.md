---
id: INFO-005
type: info
title: Dependency direction
summary: Consumes pyfmi_interfaces and pyssp_standard; neither depends on this repo
date: 2026-11-23
status: current
---

# Dependency direction

Dependencies point one way: `pyfmi_scenario` consumes the shared FMI libraries, and neither library imports it.

- **`pyfmi_interfaces`:** owns the reduction model, FMI 2.0 XML serialization, C headers, C++ entry points, FMI headers, and `.fmu` packaging.
- **`pyssp_standard`:** owns the FMI 2.0 XML objects and the archive and parameter-set facades.
- **This repository:** owns the scenario grammar, the reference evaluator, the five model hooks, and the CMake build.
- **No upstream extension:** scenario data stays in the `scenario_input` String parameter; the repository does not extend `FmuMetadata` or add `pyssp_*` control attributes upstream.
- **No reverse import:** neither shared library imports or special-cases `pyfmi_scenario`.
