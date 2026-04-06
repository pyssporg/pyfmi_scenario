#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image_name="${SCENARIO_FMU_IMAGE:-scenario-fmu:ubuntu22-gcc13}"

baseline="$(sed -n 's/.*"baseline": "\(.*\)".*/\1/p' "${repo_root}/vcpkg-configuration.json")"

if [[ -z "${baseline}" ]]; then
    echo "Failed to read vcpkg baseline from vcpkg-configuration.json" >&2
    exit 1
fi

docker build \
    --build-arg "VCPKG_COMMIT=${baseline}" \
    -f "${repo_root}/docker/ubuntu22-gcc13/Dockerfile" \
    -t "${image_name}" \
    "${repo_root}"
