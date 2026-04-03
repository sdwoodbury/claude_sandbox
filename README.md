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
in `~/.claude/CLAUDE.md` add this:
```
### Rules for Vendor Folder
- **NEVER** search, read, or index the `/vendor` directory.
- **NEVER** modify files in `/vendor`.
- If a dependency seems broken, ask the user to re-run `cargo vendor`.

## Code Navigation Rules
- **NEVER** use `grep` or `rg` for semantic symbol discovery (functions, structs, traits).
- **ALWAYS** prioritize `rust-analyzer` (ra_tool) for:
    - `find_definition`: To jump directly to the source.
    - `find_references`: To assess the blast radius of a change.
    - `type_definition`: To resolve complex trait bounds or generics.
- **Fallback:** If `rust-analyzer` fails (e.g., due to a broken build or complex macros), only then use a targeted `grep` on specific modules.

## File Ingestion Strategy
- **Threshold Rule:** For any file >500 lines, **DO NOT** use `read_file`. 
- **The Workflow:**
    1. **Discovery:** Use `rust-analyzer` to get the line number of the target symbol.
    2. **Contextual Read:** Use `context-mode` (specifically the `peek` or `summary` tools) to read only the lines surrounding the target (e.g., +/- 50 lines).
    3. **Structural Mapping:** Use `list_symbols` or `context-mode`'s `summary` to map the file's layout before proposing large edits.

## Editing Strategy
- **Surgical Edits:** Propose edits based on the specific line numbers provided by `rust-analyzer`.
- **Verification:** After editing, use `rust-analyzer` again to ensure no new type errors were introduced (run `cargo check` if necessary).
- **Final Read:** Use `read_file` only as a final "sanity check" once the file has been surgically modified and reduced in size.
```

to edit `~/.claude/config.json`, run this: `claude mcp add context-mode -- /usr/bin/context-mode`

# local rust configuration
run `cargo vendor`
then in `.cargo/config.toml` add this:
```
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
```
