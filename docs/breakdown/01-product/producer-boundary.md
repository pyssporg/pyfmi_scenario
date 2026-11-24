---
id: INFO-003
type: info
title: Producer boundary
summary: Emits one FMI 2.0 CS FMU; does not parse SysML or assemble SSP
date: 2026-11-23
status: current
---

# Producer boundary

This repository produces a scenario FMU and nothing above it.

- **Producer only:** it does not parse SysML, does not read a system model, and does not assemble an SSP.
- **No SSP artifacts:** it emits no SSD, SSV, SSM, or SSP; the SSV helper writes a single parameter set for `scenario_input`.
- **Consumer:** `pyssp_sysml` consumes the packaged FMU when a system is assembled.
- **FMI scope:** FMI 2.0 Co-Simulation only; FMI 3.0 and Model Exchange are not produced.
- **Data path:** scenario data must arrive through the String parameter; the generated runtime cannot use resource location.
- **FMI plumbing:** XML objects, C headers, CS entry points, FMI headers, and the `.fmu` zip come from `pyfmi_interfaces` and `pyssp_standard`.
