#!/usr/bin/env bash
# net_listener.sh — Low-overhead hardware network monitor for S21+ (v1.0.1)

DB_FILE="$HOME/Turbo_Takeoff/cognitive_history.db"
CONFIG_FILE="$HOME/Turbo_Takeoff/config/autopilot_config.json"
CURRENT_STATE="TERRESTRIAL_5G"

echo "📡 Starting S21+ Hardware Network Listener Daemon..."

while true; do
    # Check gateway connectivity using a fast, single-packet ping test
    if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
        DETECTED_STATE="TERRESTRIAL_5G"
        LIMIT=1048576
        INTERVAL=1.0
    else
        # No terrestrial route: transition to Starlink Direct-to-Cell Fallback
        DETECTED_STATE="SATELLITE_DIRECT_TO_CELL"
        LIMIT=1024
        INTERVAL=20.0
    fi

    # If state has transitioned, execute the control plane override
    if [ "$DETECTED_STATE" != "$CURRENT_STATE" ]; then
        echo "🚨 [STATE TRANSITION DETECTED]: $CURRENT_STATE ➡️ $DETECTED_STATE"
        TS=$(date +%s)

        # 1. Update the single-row SQLite heartbeat register
        sqlite3 "$DB_FILE" "UPDATE system_status SET network_state='$DETECTED_STATE', payload_limit_bytes=$LIMIT, last_updated=$TS WHERE id=1;"

        # 2. Log a structured safety event for our 1B Agent to analyze
        DETAILS="{\"device\":\"Samsung Galaxy S21 Plus\",\"trigger\":\"Network Interface Drop\",\"throttled_interval\":$INTERVAL}"
        sqlite3 "$DB_FILE" "INSERT INTO safety_events (timestamp, event_type, details, resolved) VALUES ($TS, 'LOSS_OF_SIGNAL_FALLBACK', '$DETAILS', 1);"

        # 3. Dynamic throttling of the configuration file on-disk using standardized --argjson
        if [ -f "$CONFIG_FILE" ]; then
            jq --argjson interval "$INTERVAL" '.daemon_settings.polling_interval_sec = $interval' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
            echo "⚙️ [SYSTEM] Throttled autopilot_config.json polling interval to ${INTERVAL}s."
        fi

        CURRENT_STATE="$DETECTED_STATE"
    fi

    # Low-frequency, hardware-friendly check loop (every 5 seconds)
    sleep 5
done
