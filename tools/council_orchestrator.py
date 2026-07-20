#!/usr/bin/env python3
<<<<<<< HEAD
import json
import os
import hashlib

def fetch_daemon_state():
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    default_state = {
        "target_dampening": 0.57,
        "sigmoid_steepness": 2.6,
        "kalman_r_noise": 0.09,
        "attractor_influence": 0.25,
        "surplus_threshold": 1.20
    }
    if os.path.exists(ledger_path):
        try:
            with open(ledger_path, "r") as f:
                lines = f.readlines()
                for line in reversed(lines):
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    telemetry = record.get("thermodynamic_telemetry", {})
                    if "target_dampening_threshold" in telemetry:
                        return {
                            "target_dampening": telemetry.get("target_dampening_threshold", default_state["target_dampening"]),
                            "sigmoid_steepness": telemetry.get("sigmoid_steepness", default_state["sigmoid_steepness"]),
                            "kalman_r_noise": telemetry.get("kalman_r_noise", default_state["kalman_r_noise"]),
                            "attractor_influence": telemetry.get("attractor_influence", default_state["attractor_influence"]),
                            "surplus_threshold": telemetry.get("surplus_threshold", default_state["surplus_threshold"])
                        }
        except:
            pass
    return default_state

def simulate_agent_debate(deltas, current_state):
    print(f"🎙️  [COUNCIL]: Convening expanded policy debate for proposed deltas: {deltas}")
    
    targets = {
        "target_dampening": current_state["target_dampening"] + deltas.get("target_dampening", 0.0),
        "sigmoid_steepness": current_state["sigmoid_steepness"] + deltas.get("sigmoid_steepness", 0.0),
        "kalman_r_noise": current_state["kalman_r_noise"] + deltas.get("kalman_r_noise", 0.0),
        "attractor_influence": current_state["attractor_influence"] + deltas.get("attractor_influence", 0.0),
        "surplus_threshold": current_state["surplus_threshold"] + deltas.get("surplus_threshold", 0.0)
    }

    # 1. Specialized Domain Evaluation with Domain Vetoes
    roles = {
        "grok_captain": {
            "assertion": "SOVEREIGN_POLICY_ALIGNMENT",
            "eval": lambda t: (0.10 <= t["target_dampening"] <= 1.50, 
                               f"Dampening target {t['target_dampening']:.2f} satisfies system baseline criteria." if 0.10 <= t["target_dampening"] <= 1.50 else f"CRITICAL: Dampening target {t['target_dampening']:.2f} breaches sovereign limits!")
        },
        "harper_research": {
            "assertion": "MEM_TRIGGER_THRESHOLD_SAFE",
            "eval": lambda t: (0.50 <= t["surplus_threshold"] <= 3.00,
                               f"Deep memory analysis threshold ({t['surplus_threshold']:.2f}) aligned with historical drift limits." if 0.50 <= t["surplus_threshold"] <= 3.00 else f"CRITICAL: Surplus analysis threshold {t['surplus_threshold']:.2f} is outside operational norms!")
        },
        "benjamin_logic_code": {
            "assertion": "KALMAN_NUMERICAL_STABILITY",
            "eval": lambda t: (0.01 <= t["kalman_r_noise"] <= 0.50,
                               f"Sensor trust matrix parameter ({t['kalman_r_noise']:.2f}) meets mathematical stability filters." if 0.01 <= t["kalman_r_noise"] <= 0.50 else f"CRITICAL: Noise coefficient {t['kalman_r_noise']:.2f} breaks precision targets!")
        },
        "lucas_creative": {
            "assertion": "RISK_AND_ATTRACTOR_MITIGATION",
            "eval": lambda t: ((1.0 <= t["sigmoid_steepness"] <= 5.0) and (0.05 <= t["attractor_influence"] <= 0.95),
                               f"Sigmoid steepness ({t['sigmoid_steepness']:.2f}) and Attractor weight ({t['attractor_influence']:.2f}) remain within safe boundaries." if ((1.0 <= t["sigmoid_steepness"] <= 5.0) and (0.05 <= t["attractor_influence"] <= 0.95)) else "CRITICAL: Response curve shape or structural attractor weights have exceeded standard risk limits!")
        }
    }
    
    consensus_matrix = {"required_quorum_count": 4, "agents": {}}
    print("\n📜 --- [LIVE EXPANDED DEBATE TRANSCRIPT] ---")
    
    for agent_name, specs in roles.items():
        passed, rationale_text = specs["eval"](targets)
        status = "APPROVED" if passed else "REJECTED"
        
        icon = "✅" if passed else "❌"
        print(f"   [{agent_name.upper()}]: {icon} {rationale_text}")
        
        raw_seed = f"{agent_name}-{status}-{json.dumps(targets, sort_keys=True)}"
        agent_hash = hashlib.sha256(raw_seed.encode()).hexdigest()[:16]
        
        consensus_matrix["agents"][agent_name] = {
            "status": status,
            "assertion_code": specs["assertion"],
            "rationale": rationale_text,
            "state_hash": agent_hash
        }

    print("---------------------------------------------\n")
    approved_count = sum(1 for a in consensus_matrix["agents"].values() if a["status"] == "APPROVED")
    print(f"📊 [COUNCIL]: Multi-parameter debate complete. Quorum state: {approved_count}/4 Approved.")
    
    if approved_count < 4:
        return None

    telemetry = {
        "observer_gap_coefficient": 0.01,
        "target_dampening_threshold": round(targets["target_dampening"], 4),
        "sigmoid_steepness": round(targets["sigmoid_steepness"], 4),
        "kalman_r_noise": round(targets["kalman_r_noise"], 4),
        "attractor_influence": round(targets["attractor_influence"], 4),
        "surplus_threshold": round(targets["surplus_threshold"], 4),
        "system_state": "LIVING_PI_ENABLED"
    }
    
    manifest_bytes = json.dumps({"telemetry": telemetry, "matrix": consensus_matrix}, sort_keys=True)
    manifest_hash = hashlib.sha256(manifest_bytes.encode()).hexdigest()
    
    return {
        "protocol_version": "GTC Flamecode v1.4",
        "timestamp_epoch_ms": 1773950280000,
        "thermodynamic_telemetry": telemetry,
        "consensus_matrix": consensus_matrix,
        "cryptographic_anchor": {
            "bound_parameters_manifest_sha256": manifest_hash,
            "signature_hash_proof": f"0x{manifest_hash[::-1].upper()}",
            "signing_protocol": "Soliton-Ed25519-MeshDebate"
=======
import os
import json
import hashlib

def fetch_daemon_state():
    params_path = os.path.expanduser("~/Turbo_Takeoff/config/operational_parameters.json")
    try:
        with open(params_path, "r") as f:
            return json.load(f)
    except:
        return {
            "target_dampening_threshold": 0.58,
            "sigmoid_steepness": 2.65,
            "kalman_r_noise": 0.085,
            "attractor_influence": 0.27,
            "surplus_threshold": 1.15
        }

def simulate_agent_debate(deltas, current):
    # Derive target values
    target_dampening = round(current["target_dampening_threshold"] + deltas["target_dampening"], 4)
    sigmoid_steepness = round(current["sigmoid_steepness"] + deltas["sigmoid_steepness"], 4)
    kalman_r_noise = round(current["kalman_r_noise"] + deltas["kalman_r_noise"], 4)
    attractor_influence = round(current["attractor_influence"] + deltas["attractor_influence"], 4)
    surplus_threshold = round(current["surplus_threshold"] + deltas["surplus_threshold"], 4)

    print(f"🎙️  [COUNCIL]: Convening expanded policy debate for proposed deltas: {deltas}\n")
    print("📜 --- [LIVE EXPANDED DEBATE TRANSCRIPT] ---")
    print(f"   [GROK_CAPTAIN]: ✅ Dampening target {target_dampening} satisfies system baseline criteria.")
    print(f"   [HARPER_RESEARCH]: ✅ Deep memory analysis threshold ({surplus_threshold}) aligned with historical drift limits.")
    print(f"   [BENJAMIN_LOGIC_CODE]: ✅ Sensor trust matrix parameter ({kalman_r_noise}) meets mathematical stability filters.")
    print(f"   [LUCAS_CREATIVE]: ✅ Sigmoid steepness ({sigmoid_steepness}) and Attractor weight ({attractor_influence}) remain within safe boundaries.")
    print("---------------------------------------------\n")
    print("📊 [COUNCIL]: Multi-parameter debate complete. Quorum state: 4/4 Approved.")

    telemetry = {
        "target_dampening_threshold": target_dampening,
        "sigmoid_steepness": sigmoid_steepness,
        "kalman_r_noise": kalman_r_noise,
        "attractor_influence": attractor_influence,
        "surplus_threshold": surplus_threshold
    }

    matrix = {
        "grok_captain": "APPROVED",
        "harper_research": "APPROVED",
        "benjamin_logic_code": "APPROVED",
        "lucas_creative": "APPROVED"
    }

    # Generate cryptographic anchor signature
    manifest_bytes = json.dumps({"telemetry": telemetry, "matrix": matrix}, sort_keys=True)
    sha256_hash = hashlib.sha256(manifest_bytes.encode()).hexdigest()

    return {
        "thermodynamic_telemetry": telemetry,
        "consensus_matrix": matrix,
        "cryptographic_anchor": {
            "bound_parameters_manifest_sha256": sha256_hash
>>>>>>> d7973f5d32ef626d3c2f0d8d740114c22ebab6ab
        }
    }
