#!/usr/bin/env python3
# inject_noise.py — Manifold Turbulence and Noise Injector Utility (v1.0.0)
import os
import json
import time
import random
import math

def inject_turbulence():
    repo_dir = os.path.expanduser("~/Turbo_Takeoff")
    telemetry_path = os.path.join(repo_dir, "platform_telemetry.json")

    if not os.path.exists(telemetry_path):
        print("❌ Telemetry file missing. Ensure the plotter or daemon is running first.")
        return

    print("🚨 [NOISE INJECTOR]: Commencing high-amplitude coordinate turbulence strike!")
    
    # 10-second decaying oscillation strike
    duration = 10.0
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            # Decaying envelope: starts high (amplitude 3.5) and decays exponentially
            envelope = 3.5 * math.exp(-0.4 * elapsed)
            
            # High frequency noise perturbation
            noise_x = math.sin(time.time() * 12.0) * envelope + random.uniform(-0.5, 0.5)
            noise_y = math.cos(time.time() * 10.0) * envelope + random.uniform(-0.5, 0.5)
            noise_z = math.sin(time.time() * 8.0) * envelope
            
            try:
                with open(telemetry_path, "r") as f:
                    state = json.load(f)
            except:
                continue

            # Apply coordinate shift
            state["coordinates"] = {
                "X": round(noise_x, 4),
                "Y": round(noise_y, 4),
                "Z": round(noise_z, 4)
            }
            # Set trust level to unstable to simulate detection
            state["system_trust_level"] = "UNSTABLE_COORDINATES"
            state["event"] = "TURBULENCE_DETECTED"
            
            with open(telemetry_path, "w") as f:
                json.dump(state, f, indent=2)
                
            # Print a neat console loading line
            bars = int((elapsed / duration) * 20)
            progress = "█" * bars + "░" * (20 - bars)
            print(f"\r⚡ [STRIKE PROGRESS]: [{progress}] Dampening Envelope: {envelope:.2f}", end="")
            
            time.sleep(0.05)
            
        print("\n🏆 [NOISE INJECTOR]: Turbulence strike complete. System returning to ambient tracking.")
        
        # Reset trust state
        try:
            with open(telemetry_path, "r") as f:
                state = json.load(f)
            state["system_trust_level"] = "NOMINAL"
            state["event"] = "ACTIVE_OPTIMIZING"
            with open(telemetry_path, "w") as f:
                json.dump(state, f, indent=2)
        except:
            pass
            
    except KeyboardInterrupt:
        print("\n💤 Strike terminated early by operator.")

if __name__ == "__main__":
    inject_turbulence()
