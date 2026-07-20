#!/usr/bin/env python3
# manifold_plotter.py — Real-Time Plotter with Integrated SQLite State Persistence (v1.2.0)
import os
import sys
import json
import time
import math
from db_manager import ManifoldDatabase

class ManifoldPlotter:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.broker_state_path = os.path.join(self.repo_dir, "platform_telemetry.json")
        self.db = ManifoldDatabase()
        
        self.history_limit = 50
        self.x_history = []
        self.y_history = []
        self.z_history = []
        self.blocks = [" ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def load_telemetry(self) -> dict:
        if not os.path.exists(self.broker_state_path):
            return {}
        try:
            with open(self.broker_state_path, "r") as f:
                return json.load(f)
        except:
            return {}

    def save_telemetry_state(self, state: dict):
        try:
            with open(self.broker_state_path, "w") as f:
                json.dump(state, f, indent=2)
        except:
            pass

    def render_sparkline(self, data: list) -> str:
        if not data:
            return "[ No Signal Data ]"
        min_v = min(data)
        max_v = max(data)
        span = max_v - min_v
        if span == 0:
            return "█" * len(data)
        sparkline = []
        for val in data:
            idx = int(((val - min_v) / span) * 7)
            sparkline.append(self.blocks[idx])
        return "".join(sparkline).ljust(self.history_limit)

    def draw_phase_space_plane(self, x_curr: float, y_curr: float, nodes: list) -> list:
        width = 40
        height = 12
        grid = [[" " for _ in range(width)] for _ in range(height)]
        
        x_min, x_max = -5.0, 5.0
        y_min, y_max = -5.0, 5.0
        
        def to_grid(x, y):
            col = int(((x - x_min) / (x_max - x_min)) * (width - 1))
            row = int(((y - y_min) / (y_max - y_min)) * (height - 1))
            row = (height - 1) - row
            return col, row

        c_col, c_row = to_grid(0, 0)
        if 0 <= c_row < height:
            for c in range(width):
                grid[c_row][c] = "─"
        if 0 <= c_col < width:
            for r in range(height):
                if grid[r][c_col] == "─":
                    grid[r][c_col] = "┼"
                else:
                    grid[r][c_col] = "│"

        for label, nx, ny in nodes:
            col, row = to_grid(nx, ny)
            if 0 <= col < width and 0 <= row < height:
                grid[row][col] = "Ⓜ" if "nine" in label else "Ⓐ"

        curr_col, curr_row = to_grid(x_curr, y_curr)
        if 0 <= curr_col < width and 0 <= curr_row < height:
            grid[curr_row][curr_col] = "🎯"

        return grid

    def execute_plotting_loop(self):
        print("⚡ Warming up high-density Termux plot canvas...")
        try:
            while True:
                tel = self.load_telemetry()
                
                # Load attractor nodes from our SQLite instance
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT label, x, y FROM attractor_nodes")
                db_nodes = cursor.fetchall()
                conn.close()

                status = tel.get("status", {})
                gain = status.get("gain", 1.0)
                damp = status.get("dampening", 0.5)
                trust = tel.get("system_trust_level", "UNKNOWN")
                event = tel.get("event", "UNKNOWN")
                limits = tel.get("dynamic_limits", {})
                scale = limits.get("active_scale", 1.0)
                
                curr_coords = tel.get("coordinates", {})
                x_val = curr_coords.get("X", None)
                y_val = curr_coords.get("Y", None)
                z_val = curr_coords.get("Z", None)

                if x_val is None:
                    x_val = math.sin(time.time() * 0.5) * (3.0 * scale)
                    y_val = math.cos(time.time() * 0.3) * (2.0 * scale)
                    z_val = math.sin(time.time() * 0.1) * 2.0
                
                # Update rolling terminal sparklines
                self.x_history.append(x_val)
                self.y_history.append(y_val)
                self.z_history.append(z_val)
                
                if len(self.x_history) > self.history_limit:
                    self.x_history.pop(0)
                    self.y_history.pop(0)
                    self.z_history.pop(0)

                # 💾 SQLite WAL Logging
                self.db.log_trajectory(x_val, y_val, z_val, gain, damp, trust, event)

                # Update state broadcast file
                tel["coordinates"] = {"X": x_val, "Y": y_val, "Z": z_val}
                tel["status"] = {"gain": gain, "dampening": damp}
                tel["system_trust_level"] = trust
                tel["event"] = event
                tel["dynamic_limits"] = limits
                self.save_telemetry_state(tel)

                # Format terminal display
                os.system("clear")
                print("=" * 64)
                print("🦅  TORDIAL MANIFOLD REAL-TIME TRAJECTORY MONITOR")
                print("=" * 64)
                print(f"📡 STATE FEEDBACK:")
                print(f"   -> Mode: {event:<25} | Trust Level: {trust}")
                print(f"   -> Loop Gain: {gain:.4f} | Dampening: {damp:.4f} | Scale: {scale:.2f}")
                print("-" * 64)
                
                print("📈 COORDINATE OSCILLATION OVER TIME:")
                print(f"   [X-Axis]: {self.render_sparkline(self.x_history)} ({x_val:+.2f})")
                print(f"   [Y-Axis]: {self.render_sparkline(self.y_history)} ({y_val:+.2f})")
                print(f"   [Z-Axis]: {self.render_sparkline(self.z_history)} ({z_val:+.2f})")
                print("-" * 64)
                
                print("🌌 2D PHASE SPACE PROJECTION MAP (X vs Y):")
                grid = self.draw_phase_space_plane(x_val, y_val, db_nodes)
                for row in grid:
                    print("   " + "".join(row))
                print("-" * 64)
                print("🎯 = Current Position | Ⓐ = Attractor Anchor | Ⓜ = Memory Inject")
                print("Press Ctrl+C to terminate real-time plotting loop...")
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n💤 Plotter canvas disconnected cleanly.")

if __name__ == "__main__":
    plotter = ManifoldPlotter()
    plotter.execute_plotting_loop()
