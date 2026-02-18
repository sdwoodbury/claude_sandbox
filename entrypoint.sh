#!/bin/bash
set -e
# uncomment these to install plugins
#exec /usr/sbin/capsh --drop=cap_net_admin --user=root -- -c "exec /bin/bash --login -i"
#exit 0
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

# Critical: Temporary DNS Allow for Resolution
# This ensures 'dig' works in the next step.
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT

# Resolve and allow specific domains
ALLOWED_DOMAINS=(
    "github.com" "api.github.com" "registry.npmjs.org"
    "api.anthropic.com" "sentry.io" "statsig.anthropic.com"
    "statsig.com" "marketplace.visualstudio.com"
    "vscode.blob.core.windows.net" "update.code.visualstudio.com"
)

for domain in "${ALLOWED_DOMAINS[@]}"; do
    # Resolve IPs (Simple fallback if DNS isn't ready yet)
    ips=$(dig +short "$domain" | grep -E '^[0-9.]+$')
    if [ -z "$ips" ]; then
        echo "⚠️ Warning: Could not resolve $domain"
        continue
    fi
    for ip in $ips; do
        iptables -A OUTPUT -d "$ip" -j ACCEPT
    done
done

# close temporary dns hole
iptables -D OUTPUT -p udp --dport 53 -j ACCEPT

# Allow DNS only to Google and Cloudflare
# This allows resolving allowed domains but prevents exfiltration to rogue DNS servers
TRUSTED_DNS=("8.8.8.8" "8.8.4.4" "1.1.1.1" "1.0.0.1")

for dns in "${TRUSTED_DNS[@]}"; do
    # Standard DNS (UDP)
    iptables -A OUTPUT -p udp -d "$dns" --dport 53 -j ACCEPT
    # DNS over TCP (fallback for large responses)
    iptables -A OUTPUT -p tcp -d "$dns" --dport 53 -j ACCEPT
done

# Ensure the container is actually using these servers
# This forces the internal resolver to use our allowed IPs
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Block Localnet (Final Catch-all)
iptables -A OUTPUT -d 10.0.0.0/8 -j REJECT
iptables -A OUTPUT -d 172.16.0.0/12 -j REJECT
iptables -A OUTPUT -d 192.168.0.0/16 -j REJECT
iptables -A OUTPUT -d 169.254.0.0/16 -j REJECT

# --- PRIVILEGE DROP & HANDOVER ---
echo "🔒 Firewall locked. Dropping NET_ADMIN..."
# Using root user to preserve host UID mapping for files
exec /usr/sbin/capsh --drop=cap_net_admin --user=root -- -c "exec /bin/bash --login -i"
