#!/usr/bin/env python3
import os
import sys
import json

sys.path.append(os.path.expanduser('~/Turbo_Takeoff/tools'))
import council_orchestrator

def derive_policy_deltas():
    return {
        "target_dampening": 0.01,
        "sigmoid_steepness": 0.05,
        "kalman_r_noise": -0.005,
        "attractor_influence": 0.02,
        "surplus_threshold": -0.05
    }

def execute_active_governance():
    print("🦅 [GOVERNANCE]: Initializing 5-dimensional policy optimization cycle...")
    
    current_state = council_orchestrator.fetch_daemon_state()
    proposed_deltas = derive_policy_deltas()
    
    payload = council_orchestrator.simulate_agent_debate(proposed_deltas, current_state)
    if not payload:
        print("❌ [GOVERNANCE]: System Safe. Policy matrix dropped due to consensus fracture.")
        sys.exit(1)
        
    telemetry = payload["thermodynamic_telemetry"]
    
    print("🛡️  [GOVERNANCE]: Running 5-dimensional daemon boundary screening...")
    if not (0.10 <= telemetry["target_dampening_threshold"] <= 1.50): sys.exit("❌ Boundary Fault: target_dampening")
    if not (1.0 <= telemetry["sigmoid_steepness"] <= 5.0): sys.exit("❌ Boundary Fault: sigmoid_steepness")
    if not (0.01 <= telemetry["kalman_r_noise"] <= 0.50): sys.exit("❌ Boundary Fault: kalman_r_noise")
    if not (0.05 <= telemetry["attractor_influence"] <= 0.95): sys.exit("❌ Boundary Fault: attractor_influence")
    if not (0.50 <= telemetry["surplus_threshold"] <= 3.00): sys.exit("❌ Boundary Fault: surplus_threshold")
        
    print("✅ [PASS]: Entire multi-variable policy verified safe.")
    
    # 1. Flush changes directly to operational config file
    params_path = os.path.expanduser("~/Turbo_Takeoff/config/operational_parameters.json")
    try:
        with open(params_path, "w") as f:
            json.dump(telemetry, f, indent=4)
        print("💾 [CONFIG]: Parameter map successfully flushed to disk.")
    except Exception as e:
        print(f"❌ [ERROR FILE WRITE]: {e}")
        sys.exit(1)
    
    # 2. Lock into ledger wire
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    try:
        with open(ledger_path, "a") as f:
            f.write(json.dumps(payload) + "\n")
        print("🔒 [LEDGER]: Soliton policy v1.4 manifest securely appended and sealed.")
    except Exception as e:
        print(f"❌ [ERROR LEDGER WRITE]: {e}")
        sys.exit(1)
        
    print("⚡ [CONTROL]: Micro-adjustments committed. Policy optimization sequence successful.")

if __name__ == "__main__":
    execute_active_governance()
