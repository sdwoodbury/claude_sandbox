Claude Sandbox


## Overview
This repository extends the sandbox provided by [Anthropic](https://github.com/anthropics/claude-code/tree/main/.devcontainer) to do the following:
- install Rust
- use docker compose to attach volumes for the cargo cache and claude credentials and configuration
- add convenience scripts to launch the container

## Build Instructions
`docker build -t claude-base -f anthropic/Dockerfile.claude_base anthropic`
`docker build -t claude -f Dockerfile.claude .`

create `~/.claude.json` and `~/.config/claude-code/auth.json`

add `/scripts` to your path

then use `claude_up.sh` and `claude_down.sh` at will


## Assumptions
docker is installed and set up to run without root. same for docker compose.

The rust version is hardcoded in `Dockerfile.claude` but can be updated
