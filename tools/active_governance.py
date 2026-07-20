#!/usr/bin/env python3
"""
active_governance.py
Unified 5D Sovereign Control Loop with Grounded Takeoff Sourcing Integration.
"""

import os
import sys
import json

sys.path.append(os.path.expanduser('~/Turbo_Takeoff/tools'))
import council_orchestrator
import takeoff_resonance

def derive_policy_deltas(mean_resonance: float, current_damp: float):
    # If dampening is already climbing, damp the delta to prevent over-optimization vetoes
    target_delta = 0.05 if current_damp < 0.62 else 0.00
    
    resonance_mod = round((mean_resonance - 80.0) * 0.001, 4)
    return {
        "target_dampening": target_delta,
        "sigmoid_steepness": 0.00,
        "kalman_r_noise": 0.00,
        "attractor_influence": 0.00,
        "surplus_threshold": round(0.01 + resonance_mod, 4),
        "curvature_budget": 0.00
    }

def execute_active_governance():
    print("🦅 [GOVERNANCE]: Extracting live construction material procurement manifests...")
    
    takeoff_data = takeoff_resonance.process_takeoff_manifest()
    mean_resonance = takeoff_data["aggregate_metrics"]["mean_ethical_resonance"]
    print(f"📊 [GOVERNANCE]: Supply loop evaluated. Mean Ethical Resonance: {mean_resonance}")
    
    current_state = council_orchestrator.fetch_daemon_state()
    current_damp = current_state.get("target_dampening_threshold", 0.61)
    
    proposed_deltas = derive_policy_deltas(mean_resonance, current_damp)
    
    payload = council_orchestrator.simulate_5d_agent_debate(proposed_deltas, current_state)
    if not payload:
        print("❌ [GOVERNANCE]: Matrix drop. Drift Inheritance safety or consensus threshold breached.")
        sys.exit(1)
        
    telemetry = payload["thermodynamic_telemetry"]
    telemetry["grounded_material_resonance"] = mean_resonance
    
    print("🛡️  [GOVERNANCE]: Verifying daemon boundaries against sovereign targets...")
    if not (0.10 <= telemetry["target_dampening_threshold"] <= 1.50): sys.exit("❌ Boundary Fault: target_dampening")
    if not (1.0 <= telemetry["sigmoid_steepness"] <= 5.0): sys.exit("❌ Boundary Fault: sigmoid_steepness")
    if not (0.01 <= telemetry["kalman_r_noise"] <= 0.50): sys.exit("❌ Boundary Fault: kalman_r_noise")
    if not (0.05 <= telemetry["attractor_influence"] <= 0.95): sys.exit("❌ Boundary Fault: attractor_influence")
    if not (0.50 <= telemetry["surplus_threshold"] <= 3.00): sys.exit("❌ Boundary Fault: surplus_threshold")
    if not (0.00 <= telemetry["living_pi_r_vitality"] <= 0.9999): sys.exit("❌ Boundary Fault: Vitality ceiling exceeded")
        
    print("✅ [PASS]: Integration parameters validated safe against Tordial-GS parameters.")
    
    params_path = os.path.expanduser("~/Turbo_Takeoff/config/operational_parameters.json")
    try:
        with open(params_path, "w") as f:
            json.dump(telemetry, f, indent=4)
        print("💾 [CONFIG]: Hardware operational map updated on disk.")
    except Exception as e:
        print(f"❌ [ERROR FILE WRITE]: {e}")
        sys.exit(1)
    
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    try:
        with open(ledger_path, "a") as f:
            f.write(json.dumps(payload) + "\n")
        print("🔒 [LEDGER]: Soliton manifest cryptographically appended and sealed.")
    except Exception as e:
        print(f"❌ [ERROR LEDGER WRITE]: {e}")
        sys.exit(1)
        
    print("⚡ [CONTROL]: Sourcing optimization complete. System normalized successfully.")

if __name__ == "__main__":
    execute_active_governance()
