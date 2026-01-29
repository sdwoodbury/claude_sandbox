Claude Sandbox

## Project Overview

This is a Docker-based sandbox environment for running Claude Code with Rust support and network isolation. It extends Anthropic's official devcontainer with additional tooling and security features.

## Build Commands

```bash
# Build base image (Node.js 20, dev tools, Claude Code CLI)
docker build -t claude-base -f anthropic/Dockerfile.claude_base anthropic

# Build application image (adds Rust 1.89.0, CMake, protobuf)
docker build -t claude -f Dockerfile.claude .

# Initialize credential files (required before first run)
touch ~/.claude.json && touch ~/.config/claude-code/auth.json

# For signing git commits - need to populate this file
touch ~/.gitconfig.claude
```

## Running the Container

```bash
# Add scripts directory to PATH, then:
claude_up        # Locked-down default (git read-only)
claude_up -r     # Add Rust target/cargo volumes
claude_up -g     # Enable git write access
claude_up -r -g  # Both extensions
```

## Architecture

**Layered Docker Build:**
1. `anthropic/Dockerfile.claude_base` - Base layer with Node.js, git, zsh, GitHub CLI, Claude Code CLI
2. `Dockerfile.claude` - Application layer adding Rust toolchain, CMake, system dependencies

**Docker Compose (modular):**
- `docker-compose.yml` - Base config: code mount, Claude auth, git read-only
- `docker-compose.rust.yml` - Adds Rust target/cargo volumes
- `docker-compose.git-rw.yml` - Git write access with SSH agent forwarding
- Runs as `node:node` with dropped capabilities and `no-new-privileges`

**Network Security (`anthropic/init-firewall.sh`):**
- Whitelist-based firewall using iptables/ipset
- Allows: GitHub, npm registry, Anthropic API, VS Code marketplace
- Blocks all other outbound traffic by default

## Key Files

- `docker-compose.yml` - Base container config (locked-down default)
- `docker-compose.rust.yml` - Rust extension (target/cargo volumes)
- `docker-compose.git-rw.yml` - Git write extension (SSH agent, gitconfig)
- `anthropic/devcontainer.json` - VS Code devcontainer configuration
- `anthropic/init-firewall.sh` - Network firewall initialization
- `scripts/claude_up` - Container lifecycle script

## Git Commit Support

Use `-g` flag to enable git commits via SSH agent forwarding. Requires `~/.gitconfig.claude`.

### Setting Up SSH Signing

1. Get your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Output: ssh-ed25519 AAAA...xyz you@example.com
   ```

2. Create `~/.gitconfig.claude`:
   ```ini
   [user]
       name = Your Name
       email = you@example.com
       signingkey = key::ssh-ed25519 AAAA...xyz you@example.com

   [gpg]
       format = ssh

   [commit]
       gpgsign = true
   ```

   The `key::` prefix tells git to match by public key content rather than file path. This works with the forwarded SSH agent since the actual key file doesn't exist in the container.

3. Ensure your SSH agent has the key loaded:
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ssh-add -l  # verify it's loaded
   ```

4. Run with git support:
   ```bash
   claude_up -g
   ```
