# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-24

### Changed (breaking)

- Renamed the distribution, import package, and console script from
  `pyfmu-scenario`/`pyfmu_scenario` to `pyfmi-scenario`/`pyfmi_scenario`.

### Added

- A `tests` workflow that lints and runs the pytest suite on Python 3.11 and
  3.12 with `cmake` and `g++` available.
- A `wheels` workflow that builds the sdist and pure-Python wheel, checks the
  version tag, and attaches both artifacts to a `v*` release.
- Product-breakdown leaves for the product, architecture, implementation,
  verification, and operation layers.

### Changed

- Adopted the pyssporg repository structure: the `src/` package layout, the
  core repository artifacts, and the two CI workflows.
- Moved the scenario producer from the prototype `scenario_fmu` package to
  `pyfmi_scenario`, with `scenario_input` as the only FMU parameter.
- Pinned `pyfmi-interfaces` to its `v0.5.3` release wheel.

## [0.1.1] - 2026-11-23

### Fixed

- Ship `pyfmi_scenario/_runtime/scenario_model.cpp` as wheel package data, so an
  installed producer can package an FMU. The 0.1.0 wheel looked for the hook in
  a source-checkout path.

## [0.1.0] - 2026-11-23

### Added

- Scenario grammar parsing and canonical serialization for `scenario_input`.
- A pure-Python reference evaluator for the `L`, `ZOH`, and `NN` interpolation
  modes.
- An FMI 2.0 Co-Simulation interface model built as a `pyfmi_interfaces`
  reduction.
- `modelDescription.xml` generation through `pyssp_standard` and an SSV
  parameter-set helper for the scenario text.
- A `pyfmi-scenario` console script with `package`, `ssv`, and `run`
  subcommands.

### Changed

- Restructured the prototype repository to the pyssporg `src/` layout and the
  fixed `scenario` model identity.

### Dependencies

- The fixed default GUID and the optional GUID override rely on
  `pyfmi_interfaces` accepting an injected `ExportIdentity.guid`; this
  repository does not generate GUIDs itself.
