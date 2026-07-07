# Claude Sandbox

## Project Overview
This is a Docker-based sandbox environment for running Claude Code with Rust support, file-system isolation, and network isolation. 

This repository contains skills that allow Claude to effeciently work on large Rust code bases. While the sandbox environment has no external dependencies (besides rootles Docker), please note that the files in `agent_config/` require `narsil` and `lsp-mux`. If you only want the sandbox, you can modify the `claude_up` script, so that it does not mount the files from `agent_config/`.

**GLIBC Compatibility:** The **Ubuntu version** defined in your `Dockerfile.claude` should match the Ubuntu version of your host machine. This guarantees that your host and container share a matching `glibc` package version, which is required for the rust compilation outputs to be compatible.

Note that the version of Claude is specified in the Dockerfile. Update this line to use a different version of Claude:
```
RUN curl -fsSL https://claude.ai/install.sh | bash -s <your desired version>
```

---

## Getting Started & Custom Agents

Follow these steps to set up the repository, configure your local environment, and extend it with custom agent workflows.

### 1. Fork and Clone
First, **fork or clone this repository**:
```bash
git clone git@github.com:sdwoodbury/claude-sandbox.git
cd claude-sandbox
```

### 2. Add Scripts to Your PATH
To run the setup commands from anywhere, add the `scripts` directory to your shell profile (e.g., `~/.bashrc` or `~/.zshrc`):
```bash
export PATH="$PATH:/path/to/claude-sandbox/scripts"
```

### 3. Creating Custom Agent Files
You can create your own agent profiles and skills. Relevant folders are `agent_config/` and `agent_config/skills`.

---

## Building and Invoking `claude_up`

### Building the Sandbox
Before running the environment for the first time, build the base image and initialize your credential files:

```bash
# Build the core image used by the claude_up script
docker build -t claude -f Dockerfile.claude .
 
# Initialize credential files (required before first run)
touch ~/.claude.json && touch ~/.config/claude-code/auth.json
# Optionally copy the local claude.json to ~/.claude.json after login.

# For signing git commits - populate this file as detailed below
touch ~/.gitconfig.claude
```

### Invoking the Container
Use the `claude_up` script to launch your sandbox. You can append specific flags or target a custom agent execution route (like `agent x` or `runX` if configured):

```bash
claude_up         # Locked-down default (git read-only)
claude_up -g      # Enable git write access
claude_up -c      # Enable Cargo
claude_up -ka     # Enable kubectl + AWS (for EKS clusters)
claude_up -g -ka  # Combine multiple flags
```

---

## Software Installation

### 1. Installing `lsp-mux`
[lspmux](https://codeberg.org/p2502/lspmux) is a language server multiplexer. Install it via Cargo:
```bash
cargo install lspmux
```

### 2. Installing `narsil-mcp`
To use the `narsil-mcp` server, you must clone and compile it from the specific `sw/use_unix_socket` branch with call-graph features enabled:
```bash
git clone git@github.com:sdwoodbury/narsil-mcp.git
cd narsil-mcp
git checkout sw/use_unix_socket
cargo install . --features call-graph
```

---

## Configuration

### `lspmux` Configuration
Edit `~/.config/lspmux/config.toml`:
```toml
instance_timeout = false # default is 300 seconds
gc_interval = 10 # default
listen = ["127.0.0.1", 27631]
connect = ["127.0.0.1", 27631] # same as `listen`
log_filters = "info"
pass_environment = ["*"]
```

### Helix Editor Integration
Edit `~/.config/helix/languages.toml` to pipe your Rust development through `lspmux`:
```toml
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

### Running `lspmux` as a Service
Run `lspmux server` prior to starting your IDE, or optionally set it up to run automatically by creating the following systemd unit file at `~/.config/systemd/user/lspmux.service`:

```ini
[Unit]
Description=Language server multiplexer server
After=network.target

[Service]
Type=simple
ExecStart=/home/<username>/.cargo/bin/lspmux server
Environment="PATH=/home/<username>/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
Restart=on-failure

[Install]
WantedBy=default.target
```

### Adding a Custom MCP Server

To add a new Model Context Protocol (MCP) server to your sandbox environment, follow the same pattern used for the `patch-file` plugin.

#### Step 1: Install the Server in `Dockerfile.claude`
Open `Dockerfile.claude` and add the installation commands for your MCP server. For example, if it is a Rust tool:
```dockerfile
# Installing a custom MCP server
RUN cargo install --git [https://github.com/username/my-custom-mcp.git](https://github.com/username/my-custom-mcp.git) --branch main
```

#### Step 2: Initialize the Server in `entrypoint.sh`
Because network and file permissions lock down at runtime, you must register the MCP server automatically every time the container starts up. Open `entrypoint.sh` and add your initialization logic alongside the existing `patch-file` setup:
```bash
# Registering your custom MCP server on startup
echo "Initializing custom-mcp server..."
claude mcp add my-custom-mcp -- my-custom-mcp-binary <args>
```

#### Step 3: Rebuild the Sandbox
Once both files are updated, rebuild your Docker image to bake in the changes:
```bash
docker build -t claude -f Dockerfile.claude .
```

---

## Advanced Feature Guides

### Git Commit Support
Use the `-g` flag to enable git commits via SSH agent forwarding. This feature relies on `~/.gitconfig.claude`.

#### Setting Up SSH Signing
1. Get your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # Output: ssh-ed25519 AAAA...xyz you@example.com
   ```

2. Populate `~/.gitconfig.claude`:
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
   > **Note:** The `key::` prefix tells git to match by public key content rather than file path. This functions seamlessly with the forwarded SSH agent since the actual key file doesn't live inside the isolated container.

3. Ensure your SSH agent has the key loaded:
   ```bash
   ssh-add ~/.ssh/id_ed25519
   ssh-add -l  # verify it's loaded
   ```

4. Run with git support:
   ```bash
   claude_up -g
   ```

### Kubernetes + AWS Support (for EKS)
Use the `-ka` flag to map local infrastructure permissions into the sandbox container.

**How it works:**
* Mounts `~/.kube:/root/.kube:rw`
* Mounts `~/.aws:/root/.aws:rw`
* Extracts K8s API server URLs from kubeconfig
* Extracts AWS regions from both `~/.aws/config` and EKS cluster endpoints
* Allows AWS API endpoints through the container firewall (STS, EKS, EC2, S3, ECR)
* Enables `aws eks get-token` authentication for kubectl

```bash
# Ensure local ~/.kube and ~/.aws are configured, then run:
claude_up -ka

# Inside the container, you can now interact with your cluster:
kubectl get pods
kubectl logs my-pod
kubectl describe deployment my-app
aws eks list-clusters
```

---

## Troubleshooting & Reference

### Key Files
* `Dockerfile.claude` - Ubuntu base image installing claude, rust, cmake, and vital toolchains.
* `entrypoint.sh` - Provisions iptables and resolves addresses of allowed endpoints on container startup.
* `scripts/claude_up` - Launches `Dockerfile.claude` and drops internal networking permissions, keeping firewall rules secure.
* `scripts/claude_down` - Finds and terminates runaway sandbox containers.

### Troubleshooting Firewall/DNS Locks
The firewall locks down the specific IP addresses for allowed domains **only at startup**.

* **If connections fail:** Restart the container. This forces a fresh DNS lookup and refreshes the underlying iptables rules.
* **If IPs change mid-session:** Some services rotate their IP addresses dynamically. If a service suddenly becomes unreachable, running a quick restart cycle via `claude_up` will pick up the new addresses.

### Acknowledgments
This project uses [ra-tool.py](https://github.com/username/ra-tool) for interacting with `lspmux`. It has been modified to communicate with `lspmux` via a UNIX socket rather than stdio.
