#!/bin/bash

set -e

INTERFACE=$1
ACTION=$2

SAMBA_SERVICE=""

# Network names:
TARGET_NETWORKS=()

# Get the current SSID for the active connection
NMCLI_OUTPUT=$(nmcli --get-values=UUID --colors=no connection show --active)
CURRENT_NETWORK_NAMES=()

IS_TARGET_NETWORK=false

# Function to check if any current network name is in the target list
read -r CURRENT_NETWORK_NAMES <<< "$NMCLI_OUTPUT"

for target in "${TARGET_NETWORKS[@]}"; do
    for curr_network in "${CURRENT_NETWORK_NAMES[@]}"; do
        if [ "$curr_network" = "$target" ]; then
            IS_TARGET_NETWORK=true
            break
        fi
    done
done

case "$ACTION" in
    up|down)
        if $IS_TARGET_NETWORK ; then
            echo "Connected to a trusted network ($CURRENT_NETWORK_NAMES). Starting Samba..."
            systemctl start $SAMBA_SERVICE
        else
            echo "Not on a trusted network ($CURRENT_NETWORK_NAMES). Stopping Samba..."
            systemctl stop $SAMBA_SERVICE
        fi
        ;;
    pre-up)
        # Optional: ensure it's off before the connection is fully established
        ;;
    post-down)
        # Ensure it's off if the interface goes completely down
        systemctl stop $SAMBA_SERVICE
        ;;
esac