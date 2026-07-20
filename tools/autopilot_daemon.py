#!/usr/bin/env python3
# autopilot_daemon.py — Autopilot Daemon with Adaptive Parameter Tuning (v1.9.0)
import os
import sys
import json
import socket
import select
import time
import math
import sqlite3

sys.path.append(os.path.expanduser("~/Turbo_Takeoff/tools"))
from db_manager import ManifoldDatabase
from predictive_filter import ManifoldKalmanFilter

class AutopilotDaemon:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.socket_dir = os.path.join(self.repo_dir, "run")
        self.socket_path = os.path.join(self.socket_dir, "control.sock")
        self.telemetry_path = os.path.join(self.repo_dir, "platform_telemetry.json")
        self.db_path = os.path.join(self.repo_dir, "cognitive_history.db")
        
        self.db = ManifoldDatabase()
        self.kf = ManifoldKalmanFilter()
        
        self.gain = 1.0
        self.dampening = 0.5
        self.trust_level = "NOMINAL"
        self.event_mode = "ACTIVE_OPTIMIZING"
        
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        os.makedirs(self.socket_dir, exist_ok=True)

    def evaluate_predictive_clamp(self, est, t):
        time_to_limit = est.get("time_to_limit")
        uncertainty = est.get("uncertainty", 0.0)
        coords = est.get("coords_est", [0.0, 0.0, 0.0])
        radius = math.sqrt(coords[0]**2 + coords[1]**2 + coords[2]**2)
        
        ttl = time_to_limit if time_to_limit is not None else 10.0
        if ttl <= 0: ttl = 0.1 

        uncertainty_scalar = 1.0 + (uncertainty * 0.2)
        activation_factor = (5.0 - radius) * (ttl / uncertainty_scalar)

        try:
            sigmoid_scale = 1.0 / (1.0 + math.exp(-activation_factor))
        except OverflowError:
            sigmoid_scale = 0.0 if activation_factor < 0 else 1.0

        if radius > 3.5 or ttl < 4.0 or uncertainty > 3.0:
            self.gain = max(0.05, round(sigmoid_scale, 4))
            self.dampening = min(0.95, round(1.0 - (sigmoid_scale * 0.5), 4))
            self.trust_level = "SIGMOID_CLAMPED"
            self.event_mode = "PREDICTIVE_INTERVENTION"
        else:
            if self.event_mode == "PREDICTIVE_INTERVENTION":
                self.gain = min(1.0, round(self.gain + 0.02, 4))
                self.dampening = max(0.5, round(self.dampening - 0.02, 4))
                if self.gain >= 1.0 and self.dampening <= 0.5:
                    self.trust_level = "NOMINAL"
                    self.event_mode = "ACTIVE_OPTIMIZING"

    def process_incoming_command(self, raw_line: str) -> str:
        try:
            cmd = json.loads(raw_line.strip())
            command_type = cmd.get("command")
            
            if command_type == "ADJUST_BIAS":
                delta = float(cmd.get("bias_delta", 0.0))
                old_damp = self.dampening
                self.dampening = min(0.95, max(0.3, round(self.dampening + delta, 4)))
                return json.dumps({"status": "SUCCESS", "mode": "PROACTIVE_STABILIZATION", "previous_dampening": old_damp, "new_dampening": self.dampening})
                
            elif command_type == "ADJUST_PARAMETERS":
                # Extensible agent-driven input adaptation schema
                dampening_target = cmd.get("target_dampening")
                justification = cmd.get("justification", "None provided")
                
                old_damp = self.dampening
                if dampening_target is not None:
                    # Deterministic hardware guardrails override extreme cognitive suggestions
                    self.dampening = min(0.90, max(0.35, round(float(dampening_target), 4)))
                    
                return json.dumps({
                    "status": "ADAPTATION_APPLIED",
                    "previous_dampening": old_damp,
                    "applied_dampening": self.dampening,
                    "daemon_override_active": old_damp != self.dampening and round(float(dampening_target), 4) != self.dampening
                })
                
            return json.dumps({"status": "ACK", "current_event": self.event_mode, "system_trust_level": self.trust_level})
        except Exception as e:
            return json.dumps({"status": "ERROR", "error": str(e)})

    def compute_next_step(self):
        t = time.time()
        self.x = math.sin(t * 0.4) * 4.2
        self.y = math.cos(t * 0.2) * 3.5
        self.z = math.sin(t * 0.1) * 2.1

        est = self.kf.update([self.x, self.y, self.z])
        self.evaluate_predictive_clamp(est, t)
        
        self.db.log_trajectory(self.x, self.y, self.z, self.gain, self.dampening, self.trust_level, self.event_mode)
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                INSERT INTO predictions (timestamp, x_est, y_est, z_est, v_magnitude, uncertainty, time_to_limit)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (t, est["coords_est"][0], est["coords_est"][1], est["coords_est"][2], 
                  est["v_magnitude"], est["uncertainty"], est["time_to_limit"]))
            conn.commit()
            conn.close()
        except:
            pass

    def write_telemetry(self):
        state = {
            "coordinates": {"X": round(self.x, 4), "Y": round(self.y, 4), "Z": round(self.z, 4)},
            "status": {"gain": self.gain, "dampening": self.dampening},
            "system_trust_level": self.trust_level,
            "event": self.event_mode
        }
        try:
            with open(self.telemetry_path, "w") as f:
                json.dump(state, f, indent=2)
        except:
            pass

    def run_ipc_server(self):
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_sock.bind(self.socket_path)
        server_sock.listen(5)
        server_sock.setblocking(False)
        
        print(f"🛰️  Autopilot Daemon online with Adaptive Parameter Tuning.")
        
        connections = []
        try:
            while True:
                self.compute_next_step()
                self.write_telemetry()
                
                readable, _, _ = select.select([server_sock] + connections, [], [], 0.5)
                for s in readable:
                    if s is server_sock:
                        conn, _ = server_sock.accept()
                        conn.setblocking(False)
                        connections.append(conn)
                    else:
                        try:
                            data = s.recv(1024)
                            if data:
                                resp = self.process_incoming_command(data.decode())
                                s.sendall((resp + "\n").encode())
                            else:
                                connections.remove(s)
                                s.close()
                        except:
                            if s in connections: connections.remove(s)
                            s.close()
        except KeyboardInterrupt:
            pass
        finally:
            server_sock.close()
            if os.path.exists(self.socket_path): os.unlink(self.socket_path)

if __name__ == "__main__":
    daemon = AutopilotDaemon()
    daemon.run_ipc_server()
