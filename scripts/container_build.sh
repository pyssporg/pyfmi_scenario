#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image_name="${SCENARIO_FMU_IMAGE:-scenario-fmu:ubuntu22-gcc13}"
build_type="${BUILD_TYPE:-Release}"
build_dir="${BUILD_DIR:-build_container}"

git submodule update --init --recursive

"${repo_root}/scripts/build_container.sh"

if ! command -v podman >/dev/null 2>&1; then
    echo "Container CLI not found: podman" >&2
    exit 1
fi

run_cmd=(podman run --rm --userns=keep-id)

run_cmd+=(
    -e CC=/usr/bin/gcc-13
    -e CXX=/usr/bin/g++-13
    -e VCPKG_ROOT=/opt/vcpkg
    -v "${repo_root}:/work"
    -w /work
    "${image_name}"
    bash -lc "cmake -S . -B ${build_dir} -G Ninja \
        -DCMAKE_TOOLCHAIN_FILE=\$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake \
        -DCMAKE_BUILD_TYPE=${build_type} \
        && cmake --build ${build_dir} -j"
)

"${run_cmd[@]}"
