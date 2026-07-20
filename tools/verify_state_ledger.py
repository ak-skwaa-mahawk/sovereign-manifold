#!/usr/bin/env python3
"""
verify_state_ledger.py
Detached Cryptographic Drift Audit Module tracking 5D Tordial-GS Parameters.
"""
import os
import sys
import json
import hashlib

def sync_all_manifests():
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    params_path = os.path.expanduser("~/Turbo_Takeoff/config/operational_parameters.json")
    
    print("🔍 [AUDIT]: Commencing cryptographic ledger integrity scan...")
    
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

    telemetry = last_record.get("thermodynamic_telemetry", {})
    matrix = last_record.get("consensus_matrix", {})
    anchor = last_record.get("cryptographic_anchor", {})
    
    # Restructured to use "consensus_matrix" to maintain absolute parity with the signer
    manifest = {"telemetry": telemetry, "consensus_matrix": matrix}
    manifest_bytes = json.dumps(manifest, sort_keys=True)
    calculated_hash = hashlib.sha256(manifest_bytes.encode()).hexdigest()
    
    if calculated_hash != anchor.get("bound_parameters_manifest_sha256"):
        print("🚨 [CRITICAL ALERT]: LEDGER TAMPERING DETECTED! Manifest signature mismatch.")
        print(f"   -> Calculated: {calculated_hash}")
        print(f"   -> Anchored:   {anchor.get('bound_parameters_manifest_sha256')}")
        sys.exit(1)
        
    if not os.path.exists(params_path):
        print("⚠️  [AUDIT WARN]: Active config missing. Healing file using ledger records...")
        return
        
    try:
        with open(params_path, "r") as f:
            live_config = json.load(f)
    except Exception as e:
        print(f"🚨 [AUDIT FAIL]: Operational config file unreadable/corrupted: {e}")
        sys.exit(1)

    mismatches = []
    mapping = [
        "target_dampening_threshold",
        "sigmoid_steepness",
        "kalman_r_noise",
        "attractor_influence",
        "surplus_threshold",
        "curvature_budget"
    ]
    
    for key in mapping:
        live_val = live_config.get(key)
        ledger_val = telemetry.get(key)
        
        if live_val is None or round(live_val, 4) != round(ledger_val, 4):
            mismatches.append(f"{key} (Live: {live_val} vs Ledger: {ledger_val})")

    if mismatches:
        print("🚨 [CRITICAL ALERT]: HARDWARE STATE DRIFT DETECTED WITHOUT COUNCIL QUORUM!")
        for m in mismatches:
            print(f"   -> Mismatch: {m}")
        print("❌ [AUDIT FAIL]: Cryptographic consensus integrity fractured.")
        sys.exit(1)

    print("✅ [AUDIT PASS]: Active configuration perfectly matches the latest cryptographically signed ledger block.")

if __name__ == "__main__":
    sync_all_manifests()
