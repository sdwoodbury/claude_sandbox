#!/bin/bash
set -e

# --- PRIVILEGED SETUP (Runs as Root) ---
echo "🛡️ Initializing hardened firewall..."

# Kill IPv6 to prevent bypasses
if command -v ip6tables &> /dev/null; then
    ip6tables -P INPUT DROP
    ip6tables -P OUTPUT DROP
    ip6tables -P FORWARD DROP
fi

# Reset IPv4
iptables -F
iptables -X
iptables -P OUTPUT DROP

# Essential Infrastructure
iptables -A OUTPUT -o lo -j ACCEPT
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Temporary DNS allow for resolution (removed after domain resolution)
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT

# Block private networks before per-domain rules to prevent DNS rebinding attacks.
# Public IPs pass through these unmatched and hit the ACCEPT rules below.
iptables -A OUTPUT -d 10.0.0.0/8 -j REJECT
iptables -A OUTPUT -d 172.16.0.0/12 -j REJECT
iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT
iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT

# API domains — allow resolved IPs individually
API_DOMAINS=(
    "api.github.com" "api.anthropic.com" "sentry.io"
    "statsig.anthropic.com" "statsig.com" "registry.npmjs.org"
)

# CDN-heavy domains — allow /24 subnets to tolerate IP rotation
CDN_DOMAINS=(
    "github.com" "marketplace.visualstudio.com"
    "vscode.blob.core.windows.net" "update.code.visualstudio.com"
)

for domain in "${API_DOMAINS[@]}"; do
    ips=$(dig +short "$domain" | grep -E '^[0-9.]+$')
    if [ -z "$ips" ]; then
        echo "⚠️ Warning: Could not resolve $domain"
        continue
    fi
    for ip in $ips; do
        iptables -A OUTPUT -d "$ip/32" -j ACCEPT
    done
done

for domain in "${CDN_DOMAINS[@]}"; do
    ips=$(dig +short "$domain" | grep -E '^[0-9.]+$')
    if [ -z "$ips" ]; then
        echo "⚠️ Warning: Could not resolve $domain"
        continue
    fi
    for ip in $ips; do
        subnet=$(echo "$ip" | sed 's/\.[0-9]*$/.0/')
        iptables -A OUTPUT -d "$subnet/24" -j ACCEPT
    done
done

# Close the temporary DNS hole
iptables -D OUTPUT -p udp --dport 53 -j ACCEPT

# --- PRIVILEGE DROP & HANDOVER ---
echo "🔒 Firewall locked. Dropping NET_ADMIN..."
# Using root user to preserve host UID mapping for files
exec /usr/sbin/capsh --drop=cap_net_admin --user=root -- -c "exec /bin/bash --login -i"
