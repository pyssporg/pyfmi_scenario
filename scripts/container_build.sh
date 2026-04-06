#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image_name="${SCENARIO_FMU_IMAGE:-scenario-fmu:ubuntu22-gcc13}"
build_type="${BUILD_TYPE:-Release}"

"${repo_root}/scripts/build_container.sh"

docker run --rm \
    -u "$(id -u):$(id -g)" \
    -e CC=/usr/bin/gcc-13 \
    -e CXX=/usr/bin/g++-13 \
    -e VCPKG_ROOT=/opt/vcpkg \
    -v "${repo_root}:/work" \
    -w /work \
    "${image_name}" \
    bash -lc "git submodule update --init --recursive \
        && cmake --preset=vcpkg -DCMAKE_BUILD_TYPE=${build_type} \
        && cmake --build build -j"
