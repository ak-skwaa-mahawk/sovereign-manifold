#!/usr/bin/env python3
"""
view_telemetry_stream.py
Historical Trend and 5D Sovereign Parameter Telemetry Dashboard.
"""
import os
import json
import sys

def render_dashboard():
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    
    print("📊 --- [SOVEREIGN MANIFOLD LIVE SYSTEM MONITORS] ---")
    if not os.path.exists(ledger_path):
        print("❌ [MONITOR]: Ledger file not found. System inactive.")
        sys.exit(1)
        
    records = []
    with open(ledger_path, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))
                
    if not records:
        print("⚠️  [MONITOR]: Ledger wire is currently empty.")
        return
        
    print(f"Total Block Commitments: {len(records)}")
    print("-" * 52)
    
    # Extract historical vectors
    latest = records[-1]
    telemetry = latest.get("thermodynamic_telemetry", {})
    matrix = latest.get("consensus_matrix", {})
    
    print(f"📍 LATEST SEALED STATE INDICES:")
    print(f"   • Spatial Dampening Target : {telemetry.get('target_dampening_threshold', 'N/A')}")
    print(f"   • System Vitality Metric   : {telemetry.get('living_pi_r_vitality', 'N/A')}")
    print(f"   • Thermodynamic H-Band     : {telemetry.get('thermo_h_band', 'N/A')}")
    print(f"   • Surplus Margin Limit     : {telemetry.get('surplus_threshold', 'N/A')}")
    print(f"   • Material Resonance Index : {telemetry.get('grounded_material_resonance', 'Untracked')}%")
    print("-" * 52)
    
    print("🎙️  COUNCIL QUORUM APPROVAL VERDICT:")
    for agent, status in matrix.items():
        print(f"   [{agent.upper().ljust(17)}] -> {status} \u2713")
    print("=" * 52)

if __name__ == "__main__":
    render_dashboard()
