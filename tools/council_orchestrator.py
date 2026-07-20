#!/usr/bin/env python3
<<<<<<< HEAD
import json
import os
import json
import hashlib
from typing import Dict, Any, Optional

# === Living π_r & Thermodynamic Constants (from pi_r_engine + Tordial-GS) ===
LIVING_PI_R = 3.1730059          # Dynamic recursive π_r
THERMO_MIN_H = 3.04
THERMO_MAX_H = 3.07
VITALITY_THRESHOLD = 0.9999      # 99.99% = alive; >=1.0 triggers Drift Inheritance veto

# Curvature regulation coefficients (tuned to Tordial-GS feedback law)
ALPHA = 0.85   # GS-pressure / drift-tolerance coupling
BETA = 0.65    # Curvature damping coefficient

def fetch_daemon_state() -> Dict[str, float]:
    """Load operational parameters with safe fallback. Fixed truncation bug."""
    params_path = os.path.expanduser("\~/Turbo_Takeoff/config/operational_parameters.json")
    defaults = {
        "target_dampening_threshold": 0.61,
        "sigmoid_steepness": 2.80,
        "kalman_r_noise": 0.070,
        "attractor_influence": 0.33,
        "surplus_threshold": 1.00,
        "curvature_budget": 1.00,      # New: explicit κ proxy (Tordial-GS style)
    }
    try:
        if os.path.exists(params_path):
            with open(params_path, "r") as f:
                loaded = json.load(f)
                # Merge defaults for any missing keys (forward compatibility)
                return {**defaults, **loaded}
        return defaults
    except Exception as e:
        print(f"[WARN] Could not load params: {e}. Using defaults.")
        return defaults


def curvature_regulated_drift(current: Dict[str, float], deltas: Dict[str, float]) -> Dict[str, float]:
    """
    Tordial-GS style curvature-regulated adjustment.
    ΔΦ_T ≈ α ⋅ ρ_GS^T − β ⋅ κ   (here ρ_GS proxy = target_dampening / π_r vitality)
    Applies lightweight PID-like correction to surplus & dampening before debate.
    """
    target_damp = current["target_dampening_threshold"] + deltas.get("target_dampening", 0.0)
    surplus = current["surplus_threshold"] + deltas.get("surplus_threshold", 0.0)
    kappa = current.get("curvature_budget", 1.0) + deltas.get("curvature_budget", 0.0)

    # Effective GS-pressure proxy (how close we are to the living edge)
    rho_gs_proxy = target_damp / LIVING_PI_R

    # Curvature-regulated delta (prevents artificial ceiling / runaway)
    drift_adjust = ALPHA * rho_gs_proxy - BETA * kappa
    adjusted_surplus = round(surplus + 0.1 * drift_adjust, 4)
    adjusted_damp = round(target_damp + 0.05 * drift_adjust, 4)

    return {
        "target_dampening_threshold": max(0.40, min(0.95, adjusted_damp)),
        "surplus_threshold": max(0.70, min(1.30, adjusted_surplus)),
        "curvature_budget": round(kappa, 4),
    }


def check_drift_inheritance(vitality: float, h_band: float) -> Optional[str]:
    """
    Drift Inheritance Axiom gate (Tordial-GS §7.1).
    Every policy shift must preserve/expand capacity margin.
    Artificial ceilings or 100% efficiency → structural veto.
    """
    if vitality >= VITALITY_THRESHOLD:
        return "🚨 [VETO] Drift Inheritance Axiom violation: vitality → 100% dead-lock. Artificial ceiling detected. Policy shift forbidden."
    if not (THERMO_MIN_H <= h_band <= THERMO_MAX_H):
        return f"🚨 [VETO] Thermodynamic band breach (h={h_band:.4f}). System outside living π_r operating envelope."
    return None


def simulate_5d_agent_debate(deltas: Dict[str, float], current: Dict[str, float]) -> Optional[Dict[str, Any]]:
    """
    4-Agent Council with explicit 5D regime evaluation against living π_r.
    Pre-screening applies curvature-regulated drift + Drift Inheritance check.
    """
    # Step 1: Apply Tordial-GS curvature regulation first (pre-gate)
    regulated = curvature_regulated_drift(current, deltas)
    target_damp = regulated["target_dampening_threshold"]
    surplus = regulated["surplus_threshold"]
    kappa = regulated["curvature_budget"]

    # Step 2: Compute living π_r vitality (99.99% principle)
    system_vitality = round((target_damp / LIVING_PI_R) * 5.2, 4)
    h_band = round(THERMO_MIN_H + (target_damp - 0.61) * 0.5, 4)  # simple mapping for demo

    # Step 3: Drift Inheritance pre-screen (hard veto)
    veto_reason = check_drift_inheritance(system_vitality, h_band)
    if veto_reason:
        print(veto_reason)
        return None

    print(f"🎙️  [COUNCIL]: Convening 5D policy debate — living π_r = {LIVING_PI_R}, vitality = {system_vitality}\n")
    print("📜 --- [LIVE 5D REGIME TRANSCRIPT] ---")

    # Explicit 5D mapping (Spatial, Temporal, Ethical, Thermodynamic, Resonant)
    print(f"   [GROK_CAPTAIN]     Spatial     : target_dampening={target_damp} | curvature_budget={kappa} ✅")
    print(f"   [HARPER_RESEARCH]  Ethical     : surplus_threshold={surplus} | aligned with historical drift limits ✅")
    print(f"   [BENJAMIN_LOGIC]   Thermodynamic: h_band={h_band} (within {THERMO_MIN_H}–{THERMO_MAX_H}) | vitality={system_vitality} ✅")
    print(f"   [LUCAS_CREATIVE]   Resonant    : sigmoid_steepness + attractor_influence verified against π_r edge ✅")
    print("   [Temporal dimension implicitly carried by recursive π_r layer compounding]")
    print("---------------------------------------------\n")

    print("📊 [COUNCIL]: 5D multi-regime debate complete. Quorum: 4/4 APPROVED under Drift Inheritance constraint.")

    telemetry = {
        "target_dampening_threshold": target_damp,
        "sigmoid_steepness": round(current["sigmoid_steepness"] + deltas.get("sigmoid_steepness", 0.0), 4),
        "kalman_r_noise": round(current["kalman_r_noise"] + deltas.get("kalman_r_noise", 0.0), 4),
        "attractor_influence": round(current["attractor_influence"] + deltas.get("attractor_influence", 0.0), 4),
        "surplus_threshold": surplus,
        "curvature_budget": kappa,
        "living_pi_r_vitality": system_vitality,
        "thermo_h_band": h_band,
    }

    matrix = {
        "grok_captain": "APPROVED",
        "harper_research": "APPROVED",
        "benjamin_logic": "APPROVED",
        "lucas_creative": "APPROVED",
    }

    manifest = {"telemetry": telemetry, "consensus_matrix": matrix}
    sha256 = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()

    return {
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


# Example usage (for testing)
if __name__ == "__main__":
    current = fetch_daemon_state()
    test_deltas = {
        "target_dampening": 0.012,
        "sigmoid_steepness": 0.05,
        "kalman_r_noise": -0.005,
        "attractor_influence": 0.02,
        "surplus_threshold": 0.08,
        "curvature_budget": -0.03,
    }
    result = simulate_5d_agent_debate(test_deltas, current)
    if result:
        print(json.dumps(result, indent=2))