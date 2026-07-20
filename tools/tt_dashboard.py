#!/usr/bin/env python3
# tt_dashboard.py — Real-time Sovereign Manifold Dashboard (v1.1.0)
import os
import sys
import time
import sqlite3
import math

class TordialHUD:
    def __init__(self):
        self.db_path = os.path.expanduser("~/Turbo_Takeoff/cognitive_history.db")
        self.ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")

    def get_latest_telemetry(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Join the raw tracking frame with the corresponding Kalman prediction state
            cursor.execute("""
                SELECT t.timestamp, t.x, t.y, t.z, p.x_est, p.y_est, p.z_est, 
                       p.v_magnitude, p.uncertainty, t.trust_level, t.active_mode
                FROM trajectories t
                LEFT JOIN predictions p ON abs(t.timestamp - p.timestamp) < 0.1
                ORDER BY t.id DESC LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            return row
        except:
            return None

    def make_character_bar(self, current_val, limit_val=5.0, length=24):
        ratio = min(1.0, max(0.0, abs(current_val) / limit_val))
        filled_blocks = int(ratio * length)
        return "█" * filled_blocks + "░" * (length - filled_blocks)

    def draw_hud_plane(self):
        print("\033[?25l") # Stealth mode: hide terminal cursor
        try:
            while True:
                # Clear terminal viewport and reset cursor coordinates
                sys.stdout.write("\033[2J\033[H")
                
                metrics = self.get_latest_telemetry()
                if not metrics:
                    print("⏳ Accessing data bus channels... Checking SQLite WAL state...")
                    time.sleep(0.5)
                    continue

                ts, rx, ry, rz, ex, ey, ez, v_mag, unc, trust, mode = metrics
                
                # Dynamic fallbacks if the filter is in its warm-up window
                ex = ex if ex is not None else rx
                ey = ey if ey is not None else ry
                ez = ez if ez is not None else rz
                v_mag = v_mag if v_mag is not None else 0.0
                unc = unc if unc is not None else 0.0

                # Spatial constraint radius calculations
                measured_radius = math.sqrt(rx**2 + ry**2 + rz**2)
                estimated_radius = math.sqrt(ex**2 + ey**2 + ez**2)

                print("=====================================================================")
                print(" 🌐  TORDIAL MANIFOLD REAL-TIME 3D HUDBAR REGISTER — S21+ EDGE")
                print("=====================================================================")
                print(f"  [System Time]: {round(ts, 2)} | [Pipeline Target Mode]: \033[1;32m{mode}\033[0m")
                print(f"  [Identity Trust Register Status]: {trust}")
                print(f"  [Current Inst. Kalman Uncertainty Covariance]: {round(unc, 5)}")
                print("---------------------------------------------------------------------")
                
                # 3D Coordinate Plane Spatial Mapping
                print(f"  X-Axis Vector: {round(rx, 3): >6} Raw      │ [{self.make_character_bar(rx)}]")
                print(f"                 {round(ex, 3): >6} Filtered │ [{self.make_character_bar(ex)}]")
                print()
                print(f"  Y-Axis Vector: {round(ry, 3): >6} Raw      │ [{self.make_character_bar(ry)}]")
                print(f"                 {round(ey, 3): >6} Filtered │ [{self.make_character_bar(ey)}]")
                print()
                print(f"  Z-Axis Vector: {round(rz, 3): >6} Raw      │ [{self.make_character_bar(rz)}]")
                print(f"                 {round(ez, 3): >6} Filtered │ [{self.make_character_bar(ez)}]")
                print("---------------------------------------------------------------------")
                
                # Kinematic Constraints and Early Warning Clamping Checks
                print(f"  Current Filter Estimated Velocity Magnitude: {round(v_mag, 4)} m/s")
                print(f"  Calculated Manifold Radial Deviation:        {round(estimated_radius, 3)} / 5.0 Boundary")
                
                if estimated_radius >= 4.0 or mode == "PREDICTIVE_INTERVENTION":
                    print("  \033[1;31m🚨 [ALERT]: CRITICAL VELOCITY ACCELERATION LIMITS REACHED — CLAMP ACTIVE\033[0m")
                else:
                    print("  \033[1;34m🟢 [STATUS]: ATTRACTOR COORDINATES COMPLIANT WITH SYSTEM ENVELOPE\033[0m")
                print("=====================================================================")
                print("  Press [Ctrl + C] to collapse visual dashboard frame layer.")
                
                time.sleep(0.5)
        except KeyboardInterrupt:
            pass
        finally:
            print("\033[?25h") # Restore standard terminal cursor view

if __name__ == "__main__":
    hud = TordialHUD()
    hud.draw_hud_plane()
