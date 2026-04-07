#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image_name="${SCENARIO_FMU_IMAGE:-scenario-fmu:ubuntu22-gcc13}"
build_if_missing="${BUILD_IF_MISSING:-1}"

if ! command -v podman >/dev/null 2>&1; then
    echo "Container CLI not found: podman" >&2
    exit 1
fi

if [[ "${build_if_missing}" == "1" ]] && ! podman image exists "${image_name}"; then
    "${repo_root}/scripts/build_container.sh"
fi

if [[ $# -gt 0 ]]; then
    run_cmd=("$@")
else
    run_cmd=(bash)
fi

podman run --rm -it --userns=keep-id \
    -e CC=/usr/bin/gcc-13 \
    -e CXX=/usr/bin/g++-13 \
    -e VCPKG_ROOT=/opt/vcpkg \
    -v "${repo_root}:/work" \
    -w /work \
    "${image_name}" \
    "${run_cmd[@]}"
