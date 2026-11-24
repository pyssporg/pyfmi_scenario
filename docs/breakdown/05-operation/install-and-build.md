---
id: INFO-010
type: info
title: Install and build
summary: Editable install, sibling-wheel dependencies, test and lint commands
date: 2026-11-23
status: current
---

# Install and build

A checkout installs with one editable command; the FMU runtime is built only when packaging.

- **Python:** 3.11 or newer.
- **Install:** `python -m venv .venv`, activate it, then `pip install -e ".[dev]"`.
- **Dependencies:** `pyfmi-interfaces` comes from its release assets and `experimental_pyssp_standard` is a direct-URL wheel, so the install needs network access and must not be paired with a PyPI `pyssp_standard`.
- **Package toolchain:** `cmake` and `g++` are required to build an `.fmu`; linux64 is the first target.
- **Checks:** `python -m pytest` and `ruff check src tests examples`.
- **Runner:** `pyfmi-scenario run` needs `fmpy` from the `dev` extra.
- **Native build:** `pyfmi-scenario package` generates the sources and a `CMakeLists.txt` in a build directory and runs cmake there; `--keep-build-dir` keeps it when developing the runtime or the hook directly.
