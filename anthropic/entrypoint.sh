#!/bin/bash
set -e

# Initialize Firewall (as root)
# This requires CAP_NET_ADMIN to be passed via Docker Compose
if [ -f /usr/local/bin/init-firewall.sh ]; then
    echo "[Entrypoint] Initializing Firewall..."
    /usr/local/bin/init-firewall.sh
fi

# Create the readiness signal
touch /tmp/container_ready

# Switch to node user and execute the command
echo "setup complete. waiting for terminal to be attached"
exec tail -f /dev/null
