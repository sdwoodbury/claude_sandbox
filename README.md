Claude Sandbox

## Project Overview

This is a Docker-based sandbox environment for running Claude Code with Rust support and network isolation.

## Build Commands

```bash
# build image used by `claude_up` script
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
claude_up -g     # Enable git write access
claude_up -ka    # Enable kubectl + AWS (for EKS clusters)
claude_up -g -ka # Combine multiple flags
```

## Key Files
- `Dockerfile.claude` - Ubuntu base image, installs claude, rust, cmake, etc.
- `entrypoint.sh` - Sets up iptables and resolves addresses of allowed endpoints on container startup.
- `scripts/claude_up` - Launches `Dockerfile.claude` and removes the networking permissions, preventing the user from changing the iptables rules.
- `scripts/claude_down` - Find and terminate runaway containers

## Troubleshooting
The firewall locks in the IP addresses for allowed domains only at startup.

If connection fails: Restart the container. This forces a fresh DNS lookup and updates the iptables rules.

If IPs change: Services sometimes rotate their IP addresses while the container is running. If a service suddenly becomes unreachable, a quick restart will pick up the new addresses.

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

## Kubernetes + AWS Support (for EKS)

Use `-ka` flag to enable kubectl and AWS access for EKS clusters.

**How it works:**
- Mounts `~/.kube:/root/.kube:rw`
- Mounts `~/.aws:/root/.aws:rw`
- Extracts K8s API server URLs from kubeconfig
- Extracts AWS regions from both `~/.aws/config` and EKS cluster endpoints
- Allows AWS API endpoints through firewall (STS, EKS, EC2, S3, ECR)
- Enables `aws eks get-token` authentication for kubectl

**Setup:**
```bash
# Ensure ~/.kube and ~/.aws are configured
claude_up -ka

# Inside container:
kubectl get pods
kubectl logs my-pod
kubectl describe deployment my-app
aws eks list-clusters
```

# configuration
replace `~/.claude/CLAUDE.md` with `agent_config/CLAUDE.md`
replace `~/.claude/agents/log-scout.md` with `agent_config/log-scout.md`
replace `~/.claude/agents/rust-explorer.md` with `agent_config/rust-explorer.md`

to add the context-mode plugin, run this:
`claude mcp add context-mode -- /usr/bin/context-mode`

to configure the patch-file-mcp plugin, run this:
`claude mcp add patch-file -- patch-file-mcp --allowed-dir /`

# lspmux
`cargo install lspmux`
https://codeberg.org/p2502/lspmux

edit `~/.config/helix/languages.toml`
```
[language-server.rust-analyzer]
command = "lspmux"
args = ["client"]


[language-server.rust-analyzer.config]
cargo = { allFeatures = true, allTargets = true }
completion = { autoimport = { enable = true } }

[[language]]
name = "rust"
language-servers = [ "rust-analyzer" ]
```

edit `~/.config/lspmux/config.toml`
```
instance_timeout = false # default is 300 seconds
gc_interval = 10 # default
listen = ["127.0.0.1", 27631]
connect = ["127.0.0.1", 27631] # same as `listen`
log_filters = "info"
pass_environment = ["*"]
```

run `lspmux server` prior to starting ide


## Acknowledgments
This project uses [ra-tool.py](https://github.com/username/ra-tool) for interacting with `lspmux`. It has been modified to communicate with `lspmux` via a UNIX socket rather than stdio. 
