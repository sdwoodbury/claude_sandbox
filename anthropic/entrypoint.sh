#!/bin/bash
set -e

# 1. Initialize Firewall (as root)
# This requires CAP_NET_ADMIN to be passed via Docker Compose
if [ -f /usr/local/bin/init-firewall.sh ]; then
    echo "[Entrypoint] Initializing Firewall..."
    /usr/local/bin/init-firewall.sh
fi

# 2. Fix permissions
chown node:node /home/node/.claude /commandhistory

# 3. Create the readiness signal
touch /tmp/container_ready

# 4. Switch to node user and execute the command
echo "[Entrypoint] Dropping privileges to node user..."
exec gosu node "$@"