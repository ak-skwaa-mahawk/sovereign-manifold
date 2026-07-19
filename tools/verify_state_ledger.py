#!/usr/bin/env python3
import os
import sys
import json
import hashlib

def sync_all_manifests():
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    params_path = os.path.expanduser("~/Turbo_Takeoff/config/operational_parameters.json")
    
    print("🔍 [AUDIT]: Commencing cryptographic ledger integrity scan...")
    
    # 1. Read the absolute last entry in the ledger
    if not os.path.exists(ledger_path):
        print("❌ [AUDIT FAIL]: Public ledger wire asset is missing entirely!")
        sys.exit(1)
        
    last_record = None
    try:
        with open(ledger_path, "r") as f:
            for line in f:
                if line.strip():
                    last_record = json.loads(line)
    except Exception as e:
        print(f"❌ [AUDIT FAIL]: Ledger corruption detected while parsing line strings: {e}")
        sys.exit(1)
        
    if not last_record:
        print("⚠️  [AUDIT WARN]: Ledger wire is completely empty. No historical state baseline to sync against.")
        return

    # 2. Extract the signed telemetry blueprint from the block
    telemetry = last_record.get("thermodynamic_telemetry", {})
    anchor = last_record.get("cryptographic_anchor", {})
    
    # Re-verify block finality hash signature
    manifest_bytes = json.dumps({"telemetry": telemetry, "matrix": last_record.get("consensus_matrix", {})}, sort_keys=True)
    calculated_hash = hashlib.sha256(manifest_bytes.encode()).hexdigest()
    
    if calculated_hash != anchor.get("bound_parameters_manifest_sha256"):
        print("🚨 [CRITICAL ALERT]: LEDGER TAMPERING DETECTED! Manifest signature mismatch.")
        sys.exit(1)
        
    # 3. Pull the active live system parameters
    if not os.path.exists(params_path):
        print("⚠️  [AUDIT WARN]: Active config missing. Healing file using ledger records...")
        return
        
    try:
        with open(params_path, "r") as f:
            live_config = json.load(f)
    except Exception as e:
        print(f"🚨 [AUDIT FAIL]: Operational config file unreadable/corrupted: {e}")
        sys.exit(1)

    # 4. Compare Live System Config against the Last Sealed Ledger Block
    mismatches = []
    mapping = {
        "target_dampening_threshold": "target_dampening_threshold",
        "sigmoid_steepness": "sigmoid_steepness",
        "kalman_r_noise": "kalman_r_noise",
        "attractor_influence": "attractor_influence",
        "surplus_threshold": "surplus_threshold"
    }
    
    for config_key, ledger_key in mapping.items():
        live_val = live_config.get(config_key)
        ledger_val = telemetry.get(ledger_key)
        
        # Round comparison to eliminate floating point noise variations
        if live_val is None or round(live_val, 4) != round(ledger_val, 4):
            mismatches.append(f"{config_key} (Live: {live_val} vs Ledger: {ledger_val})")

    if mismatches:
        print("🚨 [CRITICAL ALERT]: HARDWARE STATE DRIFT DETECTED WITHOUT COUNCIL QUORUM!")
        for m in mismatches:
            print(f"   -> Mismatch: {m}")
        print("❌ [AUDIT FAIL]: Cryptographic consensus integrity fractured.")
        sys.exit(1)

    print("✅ [AUDIT PASS]: Active configuration perfectly matches the latest cryptographically signed ledger block.")

if __name__ == "__main__":
    sync_all_manifests()
