#!/usr/bin/env python3
import json
import os
import hashlib

def scan_ledger_for_exceptions(file_path):
    print(f"🕵️‍♂️ [SCANNER]: Inspecting transaction stream: {file_path}")
    if not os.path.exists(file_path):
        print("❌ [ERROR]: Ledger file target does not exist.")
        return

    corrupted_count = 0
    total_records = 0

    with open(file_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            total_records += 1
            try:
                record = json.loads(line)
                # Inspect structural payloads vs fallback timeout strings
                data = record.get("data", {})
                
                if isinstance(data, str):
                    print(f"⚠️ [LINE {line_num}]: System logged a raw string/timeout exception: '{data}'")
                    corrupted_count += 1
                    continue

                # Check for adaptation anomalies
                status = data.get("adaptation_status")
                if status == "ACK" or status == "ADAPTATION_APPLIED":
                    continue
                
                # Check for structural consensus defects if a matrix exists
                if "consensus_matrix" in record:
                    matrix = record["consensus_matrix"]
                    agents = matrix.get("agents", {})
                    if len(agents) < matrix.get("required_quorum_count", 4):
                        print(f"🚨 [LINE {line_num}]: Quorum failure detected. Incomplete agent signature map.")
                        corrupted_count += 1

            except Exception as parse_err:
                print(f"💥 [LINE {line_num}]: Raw text corruption block. JSON parse failed: {parse_err}")
                corrupted_count += 1

    print("\n--- [SCAN COMPLETE] ---")
    print(f"📊 Processed entries: {total_records} | Exceptions flagged: {corrupted_count}")

if __name__ == "__main__":
    ledger = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    scan_ledger_for_exceptions(ledger)
