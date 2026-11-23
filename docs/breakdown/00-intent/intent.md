---
id: INFO-001
type: info
title: Intent
summary: pyfmu_scenario turns scenario-grammar text into one FMI 2.0 Co-Simulation interface and a pure-Python reference evaluator, without owning SSV semantics or the generated runtime.
date: 2026-11-23
status: current
---

# Intent

`pyfmu_scenario` owns the scenario-specific layer of the Scenario FMU. It
parses the `scenario_input` grammar into typed series, evaluates that data in
pure Python as the reference oracle, describes the FMU as a
`pyfmi_interfaces` `Reduction`, and emits the FMI 2.0
`modelDescription.xml` and a minimal SSV parameter set. A later unit generates
the C++ runtime, the packaging, and the command line from that same reduction.

The package exists so scenario data behaves identically everywhere: the FMU,
the tests, and any tool that reads the format share one parser, one
serialization, and one set of interpolation rules. Scenario text is data, not
an SSP parameter mapping: the parameter set carries the text as one String
value and does not reinterpret the series.

## Commitments

- **One grammar.** `parse_scenario` and `serialize_scenario` are the only
  readers and writers of the text; model, tests, and consumers share them.
- **One evaluator.** `series.py` mirrors the upstream C++ semantics and is the
  oracle for the generated runtime. A semantic change is a deliberate edit
  here, not a second implementation elsewhere.
- **One interface model.** The FMU is described as a direct
  `pyfmi_interfaces` `Reduction`; value references, indices, and start text are
  derived from the parsed scenario, never restated.
- **One XML path.** `modelDescription.xml` is a `pyssp_standard` FMI 2 document
  serialized by `pyfmi_interfaces`; this repository does not hand-roll FMI XML.
- **Reproducible identity.** `modelName`/`modelIdentifier` are `scenario`, the
  default GUID is fixed, and the parameter start text is the canonical
  serialization of the parsed scenario.
- **Explicit refusal.** A declared but unimplemented mode, a malformed number,
  a duplicate name, or a non-monotonic time raises a typed error rather than
  being silently coerced.

## Non-goals

- Reading or writing SSP parameter-set semantics beyond one String binding;
  this is the scenario grammar, not an SSV interpretation layer.
- FMI 3.0 and Model Exchange.
- Hand-rolled FMI XML, hand-rolled `.fmu` zip packaging, or a hand-written FMI
  runtime.
- C++ code generation, build orchestration, and CLI wiring; a later unit owns
  those from the same `Reduction`.
- Cubic interpolation (`C`): declared by the grammar, rejected as unsupported.
