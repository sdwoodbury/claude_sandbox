#!/bin/bash

export CODE_MOUNT=`pwd`
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

pushd "$PROJECT_ROOT"
docker compose -f docker-compose-claude.yml up -d
CONTAINER_ID=$(docker ps | awk 'NR > 1 {print $1}')
popd

docker exec -it $CONTAINER_ID bash
