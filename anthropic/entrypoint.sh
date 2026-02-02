#!/bin/bash
set -e

# 1. Initialize Firewall (as root)
# This requires CAP_NET_ADMIN to be passed via Docker Compose
if [ -f /usr/local/bin/init-firewall.sh ]; then
    echo "[Entrypoint] Initializing Firewall..."
    /usr/local/bin/init-firewall.sh
fi

# 2. Fix permissions for the mounted volume
# Since host user (1000) maps to root (0) in rootless, 
# we need to make sure 'node' (1000) can write to it.
echo "[Entrypoint] Syncing permissions for /home/node/dev..."
chown -R node:node /home/node/dev /home/node/.claude /commandhistory

# 3. Switch to node user and execute the command
echo "[Entrypoint] Dropping privileges to node user..."
exec gosu node "$@"