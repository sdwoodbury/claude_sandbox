#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.."

pushd "$PROJECT_ROOT"
docker compose -f docker-compose-claude.yml down
popd
