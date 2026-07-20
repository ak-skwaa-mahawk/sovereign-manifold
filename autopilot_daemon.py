#!/usr/bin/env python3
# autopilot_daemon.py — Hardened, Responsive Adaptive Autopilot Daemon (v2.3.1)
import os
import sys
import json
import time
import socket
import select
import math
import traceback
from datetime import datetime, timezone

class TurboAutopilot:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.ingress_dir = os.path.join(self.repo_dir, "ingress_payloads")
        self.log_file = os.path.join(self.repo_dir, "autopilot_execution.log")
        self.config_path = os.path.join(self.repo_dir, "config/autopilot_config.json")
        self.socket_path = os.path.join(self.repo_dir, "run/control.sock")
        
        self.last_config_mtime = 0.0
        self.system_gain = 1.0
        self.modulation_offset_hz = 0.0
        self.dampening_coefficient = 0.5
        
        self.current_scale = 1.0
        self.active_gain_slew = 0.15
        self.manual_override_active = False
        
        self.server_socket = None
        self.active_connections = []
        
        self.set_default_fallback_config()
        self.load_and_validate_config()
        self.init_ipc_socket()

    def set_default_fallback_config(self):
        self.min_gain_delta = 0.02
        self.max_gain_delta = 0.25
        self.min_modulation_delta = 0.05
        self.max_modulation_delta = 0.50
        self.min_damp_delta = 0.01
        self.max_damp_delta = 0.15
        self.vel_damping_alpha = 1.2
        self.safe_gain = 1.0
        self.safe_modulation = 0.0
        self.safe_dampening = 0.8
        self.min_confidence_threshold = 0.80
        self.polling_interval_sec = 2.0

    def load_and_validate_config(self):
        if not os.path.exists(self.config_path):
            return
        try:
            mtime = os.path.getmtime(self.config_path)
            if mtime == self.last_config_mtime:
                return
            with open(self.config_path, "r") as f:
                cfg = json.load(f)

            slew = cfg.get("slew_limits", {})
            self.min_gain_delta = max(0.005, min(0.1, float(slew.get("min_gain_delta", 0.02))))
            self.max_gain_delta = max(0.05, min(1.0, float(slew.get("max_gain_delta", 0.25))))
            self.min_modulation_delta = max(0.01, min(0.2, float(slew.get("min_modulation_delta", 0.05))))
            self.max_modulation_delta = max(0.1, min(2.0, float(slew.get("max_modulation_delta", 0.50))))
            self.min_damp_delta = max(0.005, min(0.05, float(slew.get("min_damp_delta", 0.01))))
            self.max_damp_delta = max(0.05, min(0.5, float(slew.get("max_damp_delta", 0.15))))
            self.vel_damping_alpha = max(0.1, min(5.0, float(slew.get("velocity_damping_alpha", 1.2))))

            safety = cfg.get("safety_thresholds", {})
            self.safe_gain = max(0.1, min(5.0, float(safety.get("safe_gain", 1.0))))
            self.safe_modulation = max(-10.0, min(10.0, float(safety.get("safe_modulation", 0.0))))
            self.safe_dampening = max(0.0, min(1.0, float(safety.get("safe_dampening", 0.8))))
            self.min_confidence_threshold = max(0.1, min(1.0, float(safety.get("min_confidence_threshold", 0.80))))

            daemon_cfg = cfg.get("daemon_settings", {})
            self.polling_interval_sec = max(0.1, min(10.0, float(daemon_cfg.get("polling_interval_sec", 2.0))))

            self.last_config_mtime = mtime
            self.log_event("🔄 Config reloaded and validated.")
        except Exception as e:
            self.log_event(f"❌ Config parsing error: {e}")

    def init_ipc_socket(self):
        if os.path.exists(self.socket_path):
            try:
                os.unlink(self.socket_path)
            except OSError:
                pass
        try:
            self.server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.server_socket.setblocking(False)
            self.server_socket.bind(self.socket_path)
            self.server_socket.listen(5)
            self.log_event("🔌 IPC Socket initialized.")
        except Exception as e:
            self.log_event(f"❌ Failed to bind socket: {e}")

    def handle_ipc_io(self):
        if not self.server_socket:
            return
        try:
            conn, _ = self.server_socket.accept()
            conn.setblocking(False)
            self.active_connections.append(conn)
            self.log_event("🔌 Client paired.")
            self.broadcast_state_to_conn(conn, "CLIENT_HANDSHAKE_OK")
        except BlockingIOError:
            pass
        except Exception as e:
            self.log_event(f"⚠️ Socket accept error: {e}")

        dead_connections = []
        for conn in self.active_connections:
            try:
                r, _, _ = select.select([conn], [], [], 0.0)
                if r:
                    data = conn.recv(2048).decode().strip()
                    if not data:
                        dead_connections.append(conn)
                        continue
                    self.process_inbound_command(data)
            except Exception as e:
                self.log_event(f"⚠️ Connection error processing data: {e}")
                dead_connections.append(conn)

        for dead in dead_connections:
            if dead in self.active_connections:
                self.active_connections.remove(dead)
                try:
                    dead.close()
                except:
                    pass
                self.log_event("🔌 Client decoupled.")

    def process_inbound_command(self, cmd_str: str):
        self.log_event(f"📥 Received raw IPC: {cmd_str}")
        try:
            packet = json.loads(cmd_str)
            command = packet.get("command", "RAW")
            
            if command == "OVERRIDE":
                params = packet.get("parameters", {})
                self.system_gain = round(max(0.1, min(5.0, float(params.get("gain", 1.5)))), 4)
                self.dampening_coefficient = round(max(0.0, min(1.0, float(params.get("dampening", 0.3)))), 4)
                self.modulation_offset_hz = 0.5000
                self.manual_override_active = True
                self.current_scale = 0.0
                self.log_event(f"👮 OPERATOR OVERRIDE ACTIVE. Locked Gain={self.system_gain}, Damp={self.dampening_coefficient}")
                self.render_telemetry_panel("OPERATOR_OVERRIDE_ACTIVE")
                self.broadcast_system_state("OPERATOR_TAKEOVER_LOCK_ENGAGED")
                
            elif command == "RELEASE":
                self.manual_override_active = False
                self.log_event("🔄 OPERATOR RELINQUISHED CONTROL. Resuming autonomous path.")
                self.last_config_mtime = 0.0
                self.load_and_validate_config()
                self.render_telemetry_panel("ACTIVE_OPTIMIZING")
                self.broadcast_system_state("AUTONOMOUS_CONTROL_RESUMED")
                
            elif command == "RAW":
                payload = packet.get("payload", "")
                if payload == "SAFE":
                    self.trigger_fail_safe("Manual Trigger Override")
                elif payload == "RELOAD" or payload == "STATUS_QUERY":
                    self.last_config_mtime = 0.0
                    self.load_and_validate_config()
                    self.broadcast_system_state("MANUAL_CONFIG_RELOAD_SUCCESS")
        except json.JSONDecodeError:
            if cmd_str == "SAFE":
                self.trigger_fail_safe("IPC Manual Trigger Override")
            elif cmd_str == "RELOAD":
                self.last_config_mtime = 0.0
                self.load_and_validate_config()
                self.broadcast_system_state("MANUAL_CONFIG_RELOAD_SUCCESS")

    def broadcast_system_state(self, event_tag: str):
        for conn in list(self.active_connections):
            try:
                self.broadcast_state_to_conn(conn, event_tag)
            except Exception as e:
                self.log_event(f"⚠️ State broadcast failed: {e}")
                try:
                    self.active_connections.remove(conn)
                    conn.close()
                except:
                    pass

    def broadcast_state_to_conn(self, conn, event_tag: str):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_tag,
            "status": {
                "gain": self.system_gain,
                "modulation_hz": self.modulation_offset_hz,
                "dampening": self.dampening_coefficient
            },
            "dynamic_limits": {
                "active_scale": round(self.current_scale, 4),
                "active_gain_slew": round(self.active_gain_slew, 4)
            },
            "system_trust_level": "NOMINAL" if self.system_gain > 1.0 else "SAFE_RECOVERY"
        }
        conn.sendall((json.dumps(payload) + "\n").encode())

    def log_event(self, message: str):
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        sys.stderr.write(log_entry)
        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def calculate_dynamic_slew_limits(self, confidence: float, velocity: float) -> tuple:
        scale = confidence * math.exp(-self.vel_damping_alpha * abs(velocity))
        self.current_scale = max(0.0, min(1.0, scale))
        gain_slew = self.min_gain_delta + (self.max_gain_delta - self.min_gain_delta) * self.current_scale
        mod_slew = self.min_modulation_delta + (self.max_modulation_delta - self.min_modulation_delta) * self.current_scale
        damp_slew = self.min_damp_delta + (self.max_damp_delta - self.min_damp_delta) * self.current_scale
        self.active_gain_slew = gain_slew
        return gain_slew, mod_slew, damp_slew

    def enforce_slew_rate(self, current: float, target: float, max_delta: float) -> float:
        delta = target - current
        if abs(delta) > max_delta:
            step = max_delta if delta > 0 else -max_delta
            return round(current + step, 4)
        return round(target, 4)

    def trigger_fail_safe(self, reason: str):
        self.log_event(f"🚨 FAIL-SAFE ACTIVATED: {reason}")
        self.system_gain = self.safe_gain
        self.modulation_offset_hz = self.safe_modulation
        self.dampening_coefficient = self.safe_dampening
        self.current_scale = 0.0
        self.manual_override_active = False
        self.render_telemetry_panel("EMERGENCY_SAFE_MODE")
        self.broadcast_system_state("SAFETY_OVERRIDE_ACTIVE")

    def render_telemetry_panel(self, system_status: str):
        os.system("clear")
        print("=" * 64)
        print(f"✈️  TURBO_TAKEOFF ADAPTIVE AUTOPILOT [v2.3.1] - {system_status}")
        print("=" * 64)
        print(f"📡 CONTROL ENVIRONMENT:")
        print(f"   -> Operating Gain       : {self.system_gain:.4f}")
        print(f"   -> Modulation Offset    : {self.modulation_offset_hz:.4f} Hz")
        print(f"   -> Dampening Coefficient: {self.dampening_coefficient:.4f}")
        print("-" * 64)
        print(f"🧠 CONTEXT-AWARE ADAPTATION SCALING:")
        print(f"   -> Control Openness (%) : {self.current_scale * 100.0:.2f} %")
        print(f"   -> Effective Gain Slew  : {self.active_gain_slew:.4f} max/step")
        print("-" * 64)
        print(f"🎛️  SYSTEM MODE:")
        print(f"   -> Control Authority    : {'MANUAL OPERATOR' if self.manual_override_active else 'AUTONOMOUS CORE'}")
        print(f"   -> Active Client Links  : {len(self.active_connections)}")
        print("=" * 64)
        print("Press Ctrl+C to cleanly suspend autopilot...")

    def process_payload(self, file_path: str):
        if self.manual_override_active:
            return False

        try:
            with open(file_path, "r") as f:
                payload = json.load(f)
        except Exception as e:
            self.log_event(f"❌ Error reading payload: {e}")
            return False

        confidence = payload.get("confidence", 0.0)
        coords = payload.get("coordinates", {"X": 0.0, "Y": 0.0, "Z": 0.0})
        velocity = payload.get("original_signal", {}).get("translation_velocity_delta_d", 0.0)

        if confidence < self.min_confidence_threshold:
            self.trigger_fail_safe(f"Confidence score {confidence:.4f} below limit ({self.min_confidence_threshold:.2f})")
            return True

        gain_slew, mod_slew, damp_slew = self.calculate_dynamic_slew_limits(confidence, velocity)

        target_gain = round(1.0 + (coords.get("X", 0.0) / 10.0), 4)
        target_modulation = round(coords.get("Y", 0.0) * 1.5, 4)
        target_damp = round(0.5 + (coords.get("Z", 0.0) * 0.1), 4)

        self.system_gain = self.enforce_slew_rate(self.system_gain, target_gain, gain_slew)
        self.modulation_offset_hz = self.enforce_slew_rate(self.modulation_offset_hz, target_modulation, mod_slew)
        self.dampening_coefficient = self.enforce_slew_rate(self.dampening_coefficient, target_damp, damp_slew)

        self.system_gain = round(max(0.1, min(5.0, self.system_gain)), 4)
        self.dampening_coefficient = round(max(0.0, min(1.0, self.dampening_coefficient)), 4)

        self.render_telemetry_panel("ACTIVE_OPTIMIZING")
        self.broadcast_system_state("COORDINATE_STATE_OPTIMIZATION")
        return True

    def start_polling(self):
        self.log_event("🚀 Autopilot Daemon initialized.")
        self.render_telemetry_panel("MONITOR_ACTIVE")
        try:
            while True:
                # Core operational checks
                self.load_and_validate_config()
                self.handle_ipc_io()

                if not self.manual_override_active:
                    files = [os.path.join(self.ingress_dir, f) for f in os.listdir(self.ingress_dir) if f.endswith(".json")]
                    files.sort(key=os.path.getmtime)
                    for fpath in files:
                        success = self.process_payload(fpath)
                        if success:
                            os.remove(fpath)
                        time.sleep(0.1) # Small stagger

                # HIGH-RESPONSIVENESS SLEEP LOOP:
                # Sleep for 2 seconds but check the socket 40 times per cycle!
                slept = 0.0
                while slept < self.polling_interval_sec:
                    self.handle_ipc_io()
                    time.sleep(0.05)
                    slept += 0.05

        except KeyboardInterrupt:
            self.log_event("💤 Suspended.")
        except Exception as crash_error:
            # Trap all tracebacks to file before letting the finally block fire
            tb = traceback.format_exc()
            self.log_event(f"💀 FATAL CORE CRASH:\n{tb}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)

if __name__ == "__main__":
    daemon = TurboAutopilot()
    daemon.start_polling()
