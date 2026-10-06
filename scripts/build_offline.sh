#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
task_wheels="${ESHQOZI_WHEELHOUSE:-/tmp/eshqozi-wheels}"
task_docker_config="${DOCKER_CONFIG:-/tmp/eshqozi-docker}"
mkdir -p "$task_wheels" "$task_docker_config"
.venv/bin/python -m ensurepip >/dev/null
.venv/bin/python -m pip download --require-hashes --only-binary=:all: --no-cache-dir \
    -r requirements.lock --dest "$task_wheels"
DOCKER_CONFIG="$task_docker_config" docker build --build-arg DEPS_STAGE=dependencies-offline \
    --build-context "wheels=$task_wheels" -t eshqozi:local .
