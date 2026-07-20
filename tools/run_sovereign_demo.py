#!/usr/bin/env python3
"""
run_sovereign_demo.py
Unified Master Demonstration Harness for the Sovereign Manifold.
Executes an end-to-end simulation run showing calculation, 5D quorum validation, 
ledger persistence, chart generation, and narrative briefing creation.
"""

import os
import sys
import time
import subprocess
import json

def line_break():
    print("\n" + "="*60 + "\n")

def run_step(title, command_list):
    print(f"🔷 [DEMO STEP]: {title}")
    print(f"👉 Running: {' '.join(command_list)}")
    try:
        res = subprocess.run(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if res.stdout:
            print(res.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ [STEP FAILED]: {e}")
        if e.stdout: print(f"Stdout:\n{e.stdout}")
        if e.stderr: print(f"Stderr:\n{e.stderr}")
        return False

def main():
    line_break()
    print("🌟 SOVEREIGN MANIFOLD END-TO-END SYSTEM DEMONSTRATION 🌟")
    print("Initializing proof-of-concept run across the integrated stack...")
    line_break()

    # Step 1: Force parameter calibration to establish a clean operational threshold base
    success = run_step(
        "Calibrating system parameters to verify council consensus quorum alignment",
        ["python3", os.path.expanduser("~/Turbo_Takeoff/tools/calibrate_equilibrium.py")]
    )
    if not success: sys.exit(1)
    time.sleep(1)
    line_break()

    # Step 2: Trigger the complete structural estimation data pipeline
    success = run_step(
        "Executing the core takeoff pipeline (Material Shift -> 5D Gate -> Ledger -> Briefing)",
        ["python3", os.path.expanduser("~/Turbo_Takeoff/tools/process_takeoff_pipeline.py")]
    )
    if not success: sys.exit(1)
    time.sleep(1)
    line_break()

    # Step 3: Run the cryptographic zero-trust ledger integrity scan
    success = run_step(
        "Auditing the transaction ledger to guarantee state parameters remain perfectly sealed",
        ["python3", os.path.expanduser("~/Turbo_Takeoff/tools/verify_state_ledger.py")]
    )
    if not success: sys.exit(1)
    line_break()

    print("🎉 [DEMO COMPLETE]: All core integration boundaries verified successfully!")
    print("• Transaction committed securely to the persistent public ledger wire.")
    print("• Telemetry snapshot visualization saved to disk output directory.")
    print("• Cryptographically anchored local narrative briefing attestation complete.")
    line_break()

if __name__ == "__main__":
    main()
