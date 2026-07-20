#!/usr/bin/env python3
# mock_los.py — Align active S21+ configs to off-grid satellite state (v1.0.0)
import os
import sys
import sqlite3
import time
import json

DB_PATH = os.path.expanduser("~/Turbo_Takeoff/cognitive_history.db")
CONFIG_PATH = os.path.expanduser("~/Turbo_Takeoff/config/autopilot_config.json")

def simulate_loss_of_signal():
    print("📡 [TEST] Initializing Mock Loss-of-Signal (LOS) Test...")
    
    if not os.path.exists(DB_PATH):
        print("❌ [ERROR] Database not found. Initialize it first.")
        return

    # Capture configuration states
    old_config = {
        "network_state": "TERRESTRIAL_5G",
        "telemetry_polling_hz": 1.0,
        "allowed_lte_bands": [2, 25],
        "starlink_direct_to_cell": False
    }
    
    new_config = {
        "network_state": "SATELLITE_DIRECT_TO_CELL",
        "telemetry_polling_hz": 0.05,  # Throttled to match satellite bandwidth constraints
        "allowed_lte_bands": [2, 25],
        "starlink_direct_to_cell": True
    }
    
    print("📉 [TEST] Dropping terrestrial 5G... Forcing fallback to Starlink Direct-to-Cell.")
    time.sleep(1) 

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Log the safety event to match active safety_events schema
    # Active fields: timestamp, event_type, details, resolved
    print("🤖 [AGENT] Intercepting network anomaly... Executing safety protocol.")
    details_payload = {
        "old_config": old_config,
        "new_config": new_config,
        "device": "Samsung Galaxy S21 Plus"
    }
    
    cursor.execute("""
        INSERT INTO safety_events (timestamp, event_type, details, resolved) 
        VALUES (?, ?, ?, ?)
    """, (time.time(), "LOSS_OF_SIGNAL_FALLBACK", json.dumps(details_payload), 1))
    
    # 2. Inject a low-frequency trajectory record matching the throttled rate
    # Active fields: timestamp, x, y, z, gain, dampening, trust_level, active_mode
    cursor.execute("""
        INSERT INTO trajectories (timestamp, x, y, z, gain, dampening, trust_level, active_mode) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (time.time(), 0.4885, -0.4102, 0.0487, 1.0, 0.8, "NOMINAL", "FAIL_SAFE_STABILIZED"))
    
    conn.commit()
    conn.close()
    
    # 3. Physically update the local autopilot config to match the satellite polling loop
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
            cfg["daemon_settings"]["polling_interval_sec"] = 20.0  # Throttle to match satellite latency
            with open(CONFIG_PATH, "w") as f:
                json.dump(cfg, f, indent=2)
            print("⚙️  [SYSTEM] Autopilot daemon polling rate throttled to 20.0s.")
    except Exception as e:
        print(f"⚠️ [WARNING] Failed to update config file: {e}")

    print("✅ [TEST] Database injection and system throttling complete.\n")

if __name__ == "__main__":
    simulate_loss_of_signal()
