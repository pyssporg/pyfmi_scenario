# AGENTS

## Vision first (required)

Before you read code, edit files, or plan a change, read the project vision:

**`docs/breakdown/00-intent/intent.md`**

It states why this repository exists, what it commits to, and what it refuses to
become. It is the first document to read, not a reference of last resort.

- Read it in full before making any change to code, tests, docs, or artifacts.
- Judge every proposed change against it. If a change conflicts with the vision,
  its commitments, or its non-goals, stop and surface the conflict; do not
  implement it silently.
- If the work shows the long-term direction is wrong, change the vision
  deliberately first, then the code. Never let the repository drift away from
  its stated intent.

## Rules

1. **Don't assume. Surface tradeoffs.** If a contract is ambiguous, stop and say
   so rather than picking a behaviour silently.
2. **Minimum code that solves the problem.** Nothing speculative.
3. **Touch only what you must.** Clean up only your own mess.
4. **Define success criteria and verify.**

## Repository Focus

`pyfmu_scenario` turns scenario time-series text into one packaged FMI 2.0
Co-Simulation FMU. It reads the `scenario_input` grammar into typed series,
evaluates that data in pure Python as the reference oracle, describes the FMU as
a `pyfmi_interfaces` reduction, generates the FMI 2.0 runtime and
`modelDescription.xml`, and packages the `.fmu`.

- Input: one String parameter, `scenario_input`, carrying the canonical
  scenario text.
- Outputs: one Real output per declared series, named after the series, in
  declaration order.
- The Python package lives in `src/pyfmu_scenario/`; packaging writes a build
  directory with a generated `CMakeLists.txt` that compiles the runtime.
- The repository is an FMU producer only. It does not parse SysML and does not
  emit SSD, SSV, SSM, or SSP; the SSV helper writes one parameter set.
- Current state lives in `docs/breakdown/`; the code is the source of truth
  when the two disagree.

## Hard constraints

- **Never hand-roll FMI XML, `.fmu` packaging, or the FMI runtime.** Build,
  serialize, and validate through `pyfmi_interfaces` and `pyssp_standard`.
- **One grammar, one evaluator, one interface model.** `parse_scenario` and
  `serialize_scenario` are the only text readers and writers; `series.py` is
  the semantic oracle; `build_reduction` is the only interface model.
- **Deterministic artifacts.** The parameter start value is the canonical
  serialization, archive order is fixed, and no ambient clock enters an
  artifact. The same scenario produces the same bytes.
- **Output identity is fixed.** `modelName` and `modelIdentifier` are
  `scenario`, `generationTool` is `pyfmu-scenario`, and the default GUID is
  `9524b75e-dc71-47cd-a02f-e22b95a3f76d`. A GUID may be injected, never
  generated locally.
- **Producer only.** Do not add SysML parsing or SSP assembly. Do not extend
  `FmuMetadata` or add `pyssp_*` control attributes upstream; scenario data
  stays in the String parameter.
- **Build at package time.** Importing or installing the package never invokes
  a compiler. `cmake` and `g++` are required only when packaging an `.fmu`.
- **FMI 2.0 Co-Simulation only.** FMI 3.0, Model Exchange, cubic interpolation,
  and platforms beyond `linux64` are out of scope until a deliberate decision
  widens them.

## Code guidelines

- Keep changes direct and explicit. Minimize duplication without hiding the
  data flow behind abstractions.
- Keep the public surface small: typed `Scenario` data, one reduction builder,
  one XML writer, one parameter-set writer, and the CLI.
- Raise a typed `ScenarioError` subclass for malformed input; never coerce a
  defect silently.
- Treat the generated artifact as the unit under test. Assert on the emitted
  XML, the parameter set, or the packed `.fmu`.
- Keep error messages naming the input, its owner, and the offending value.
- Preserve user changes in a dirty worktree; never revert unrelated edits.

## Conventions

- `README.md` is the landing page for users; `AGENTS.md` is for contributors.
- Current state lives in `docs/breakdown/` leaves, in the present tense.
- After breakdown edits, run `python3 <pb> check --strict` and
  `python3 <pb> node-size --strict` with the product-breakdown skill's `pb`
  script.
- Version lives in `src/pyfmu_scenario/__init__.py` only; `pyproject.toml` is
  dynamic and has no `[project].version`.
- `LICENSE` keeps the upstream MIT text with its Linköping University
  copyright holder line.

## Environment

- Python >= 3.11. No virtualenv is tracked; create one per checkout.
- Install: `python -m venv .venv && .venv/bin/pip install -e ".[dev]"`. The
  runtime dependencies are not PyPI releases: `experimental_pyssp_standard` is
  a direct-URL wheel and `pyfmi-interfaces` comes from its release assets.
- Tests: `python -m pytest`; the suite includes the network-free grammar,
  evaluator, interface-model, XML, and parameter-set checks.
- Lint: `ruff check src tests examples`.
- CLI: `pyfmu-scenario package`, `pyfmu-scenario ssv`, and
  `pyfmu-scenario run`; each accepts `--help`.
- Packaging an FMU needs `cmake` and `g++`; `pyfmu-scenario package` writes the
  generated sources and `CMakeLists.txt` into a build directory and runs cmake
  there. `--keep-build-dir` keeps it for inspection.
