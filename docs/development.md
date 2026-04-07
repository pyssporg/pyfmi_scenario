# Development Notes

This page collects development-facing details without mixing them into user
onboarding docs.

## Build Targets

Primary targets:

- `scenario`: Shared library implementing the FMI 2.0 Co-Simulation API
- `scenario_tests`: GoogleTest-based test executable

## Important Paths

- `libs/scenario_fmu/include/`: Public headers
- `libs/scenario_fmu/include_private/`: Internal headers
- `libs/scenario_fmu/src/`: FMU implementation
- `test/`: Unit and integration-style tests
- `python/src/scenario_fmu_generator/`: Packaging and runner tooling

## Test Coverage Focus

Current tests exercise:

- Basic FMI 2.0 API exposure
- Instantiation and lifecycle
- Parsing of scenario input
- Output interpolation behavior
- Output derivative behavior

Run them with:

```bash
ctest --test-dir build -V
```

## Artifact Inspection

To inspect exported symbols in the built library:

```bash
objdump -TC build/libs/scenario_fmu/scenario.so
```

## Reproducible Container Build

The repository includes a Podman-based build path using Ubuntu 22.04 and
GCC 13.

Build inside the container:

```bash
./scripts/container_build.sh
```

Open a shell:

```bash
./scripts/container_shell.sh
```

The container definition lives in `containers/ubuntu22-gcc13/Containerfile`.
