#!/bin/bash
set -euo pipefail

export CODE_MOUNT="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

pushd "$PROJECT_ROOT"
docker compose -f docker-compose-claude.yml up -d
CONTAINER_ID=$(docker compose -f docker-compose-claude.yml ps -q claude)
popd

docker exec -it $CONTAINER_ID bash
