#!/usr/bin/env python3
import json
import os

def find_last_valid_state(file_path):
    print("🔄 [RECOVERY]: Initiating state rollback scanner...")
    if not os.path.exists(file_path):
        print("❌ [ERROR]: public_ledger_wire.jsonl missing.")
        return None

    valid_state = None
    
    with open(file_path, "r") as f:
        lines = f.readlines()
        
    # Scan backward from the most recent entry
    for index, line in enumerate(reversed(lines), 1):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
            data = record.get("data", {})
            
            # Skip rows containing structural string exceptions or timeouts
            if isinstance(data, str):
                continue
                
            # Enforce consensus matrix constraints if present
            if "consensus_matrix" in record:
                matrix = record["consensus_matrix"]
                agents = matrix.get("agents", {})
                if len(agents) < matrix.get("required_quorum_count", 4):
                    continue # Quorum failed, keep looking backward

            # If the entry has a signature hash proof or a nominal adaptation flag, lock it in
            if "signature_hash_proof" in record or data.get("adaptation_status") == "ADAPTATION_APPLIED":
                line_num = len(lines) - index + 1
                print(f"✅ [RECOVERY]: Valid state signature found on Line {line_num}!")
                valid_state = data
                break
        except:
            continue

    if valid_state:
        print("\n--- [ROLLBACK TARGET FOUND] ---")
        print(f"🔹 Target Dampening: {valid_state.get('target_dampening', 'N/A')}")
        print(f"🔹 Justification:    {valid_state.get('justification', 'N/A')}")
        return valid_state
    else:
        print("❌ [CRITICAL]: No valid historical state found in the ledger trail.")
        return None

if __name__ == "__main__":
    ledger = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    find_last_valid_state(ledger)
