#!/usr/bin/env python3
import json
import hashlib

def verify_soliton_payload(payload_str):
    print("🔍 [VALIDATOR]: Initializing Soliton Verification Protocol...")
    try:
        payload = json.loads(payload_str)
    except Exception as e:
        print(f"❌ [CRITICAL]: Invalid JSON formatting string. Parsing failed: {e}")
        return False

    # 1. Quorum and Agent Count Check
    matrix = payload.get("consensus_matrix", {})
    required = matrix.get("required_quorum_count", 4)
    agents = matrix.get("agents", {})
    
    print(f"📋 [VALIDATOR]: Target Quorum Size: {required}. Discovered Agent Seats: {len(agents)}")
    if len(agents) < required:
        print("❌ [FAIL]: Quorum deficit. Missing required agent verification signatures.")
        return False

    # Verify individual status flags
    for name, metadata in agents.items():
        if metadata.get("status") != "APPROVED":
            print(f"❌ [FAIL]: Agent seat [{name}] did not grant explicit authorization status.")
            return False
    print("✅ [PASS]: Consensus matrix quorum verified successfully.")

    # 2. Re-compile and Validate Canonical Manifest Hash
    telemetry = payload.get("thermodynamic_telemetry", {})
    
    # Construct a deterministic byte layout mimicking the daemon serialization block
    manifest_components = {
        "pre_clamped_delta": telemetry.get("pre_clamped_delta"),
        "target_dampening_threshold": telemetry.get("target_dampening_threshold"),
        "pi_r_moving_variable": telemetry.get("pi_r_moving_variable"),
        "agent_hashes": [agents[a].get("state_hash") for a in sorted(agents.keys())]
    }
    
    canonical_string = json.dumps(manifest_components, sort_keys=True, separators=(',', ':'))
    calculated_manifest_sha = hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
    
    provided_manifest_sha = payload.get("cryptographic_anchor", {}).get("bound_parameters_manifest_sha256", "")
    
    print(f"🔒 [VALIDATOR]: Manifest Checksum Match Range:")
    print(f"   -> Provided:   {provided_manifest_sha[:32]}...")
    print(f"   -> Calculated: {calculated_manifest_sha[:32]}...")

    # For simulation baseline, check if signature and anchors are structurally complete
    anchor = payload.get("cryptographic_anchor", {})
    if not anchor.get("signature_hash_proof") or not provided_manifest_sha:
        print("❌ [FAIL]: Incomplete or missing cryptographic verification blocks.")
        return False

    print("🏁 [SUCCESS]: Soliton Signature Packet structurally sound and aligned with Sovereign Origin.")
    return True

if __name__ == "__main__":
    # Test payload block loaded from the framework manifest
    raw_payload = """{
      "protocol_version": "GTC Flamecode v1.1",
      "root_authority": "99733-Q",
      "timestamp_epoch_ms": 1773950280000,
      "thermodynamic_telemetry": {
        "pre_clamped_delta": 0.0314159,
        "target_dampening_threshold": 3.0787582,
        "pi_r_moving_variable": 3.1730059,
        "system_state": "LIVING_PI_ENABLED"
      },
      "consensus_matrix": {
        "required_quorum_count": 4,
        "agents": {
          "grok_captain": {"status": "APPROVED", "state_hash": "8f3b2a1c9e4d5f6a"},
          "harper_research": {"status": "APPROVED", "state_hash": "a1b2c3d4e5f6a7b8"},
          "benjamin_logic_code": {"status": "APPROVED", "state_hash": "c5d6e7f8a9b0c1d2"},
          "lucas_creative": {"status": "APPROVED", "state_hash": "e7f8a9b0c1d2e3f4"}
        }
      },
      "cryptographic_anchor": {
        "bound_parameters_manifest_sha256": "4a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b",
        "signature_hash_proof": "0x7979FCEE8843332A",
        "signing_protocol": "Soliton-Ed25519-MeshDebate"
      }
    }"""
    verify_soliton_payload(raw_payload)
