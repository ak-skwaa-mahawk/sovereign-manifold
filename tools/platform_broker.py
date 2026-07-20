#!/usr/bin/env python3
# platform_broker.py — Telemetry Multiplexer & Interactive HITL Override Bridge (v1.1.0)
import os
import sys
import json
import socket
import select
import time

class PlatformBroker:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.local_socket_path = os.path.join(self.repo_dir, "run/control.sock")
        
        # Paths for system handoffs
        self.platform_log = os.path.join(self.repo_dir, "run/platform_telemetry.json")
        self.hitl_override_path = os.path.join(self.repo_dir, "run/hitl_state.json")
        
        self.last_hitl_mtime = 0.0
        self.last_intervention_state = False

    def connect_to_core(self) -> socket.socket:
        if not os.path.exists(self.local_socket_path):
            sys.stderr.write("❌ [BROKER]: Autopilot control socket not found. Awaiting daemon launch...\n")
            return None
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.local_socket_path)
            sys.stderr.write("🔌 [BROKER]: Paired with local Autopilot socket.\n")
            return sock
        except Exception as e:
            sys.stderr.write(f"❌ [BROKER]: Connection failed: {e}\n")
            return None

    def check_for_operator_intervention(self, sock: socket.socket):
        """Checks if the operator has written a manual takeover flag to hitl_state.json"""
        if not os.path.exists(self.hitl_override_path) or not sock:
            return

        try:
            mtime = os.path.getmtime(self.hitl_override_path)
            if mtime == self.last_hitl_mtime:
                return

            with open(self.hitl_override_path, "r") as f:
                hitl_data = json.load(f)

            takeover_active = hitl_data.get("operator_takeover", False)
            self.last_hitl_mtime = mtime

            if takeover_active != self.last_intervention_state:
                if takeover_active:
                    sys.stderr.write("🚨 [BROKER]: Operator Takeover Detected! Injecting override command...\n")
                    sock.sendall("OVERRIDE\n".encode())
                else:
                    sys.stderr.write("🔄 [BROKER]: Operator relinquished control. Returning to autonomous path...\n")
                    sock.sendall("RELOAD\n".encode())
                self.last_intervention_state = takeover_active

        except Exception as e:
            sys.stderr.write(f"⚠️ [BROKER]: Error reading HITL state file: {e}\n")

    def dispatch_to_platform(self, telemetry_frame: dict):
        platform_payload = {
            "source": "TORDIAL_MANIFOLD_AUTOPILOT",
            "epoch_ms": int(time.time() * 1000),
            "payload_integrity": telemetry_frame.get("system_trust_level", "UNKNOWN"),
            "dynamic_gains": {
                "proportional_gain": telemetry_frame.get("status", {}).get("gain", 1.0),
                "frequency_modulation_offset": telemetry_frame.get("status", {}).get("modulation_hz", 0.0)
            },
            "environment_damping": telemetry_frame.get("status", {}).get("dampening", 0.5),
            "adaptation_scale": telemetry_frame.get("dynamic_limits", {}).get("active_scale", 1.0)
        }
        try:
            with open(self.platform_log, "w") as f:
                json.dump(platform_payload, f, indent=2)
        except Exception as e:
            sys.stderr.write(f"❌ [BROKER]: Platform dispatch error: {e}\n")

    def dispatch_to_hitl_telemetry(self, telemetry_frame: dict):
        """Updates runtime metrics in the HITL state file without erasing intervention status flags."""
        existing_takeover = False
        if os.path.exists(self.hitl_override_path):
            try:
                with open(self.hitl_override_path, "r") as f:
                    existing_takeover = json.load(f).get("operator_takeover", False)
            except:
                pass

        hitl_payload = {
            "last_handshake": telemetry_frame.get("timestamp"),
            "operator_takeover": existing_takeover,
            "allow_operator_intervention": True if telemetry_frame.get("system_trust_level") == "NOMINAL" else False,
            "target_vectors_active": True,
            "current_gate_state": telemetry_frame.get("event", "UNKNOWN")
        }
        try:
            with open(self.hitl_override_path, "w") as f:
                json.dump(hitl_payload, f, indent=2)
            # Prevent broker from reacting to its own write actions
            self.last_hitl_mtime = os.path.getmtime(self.hitl_override_path)
        except Exception as e:
            sys.stderr.write(f"❌ [BROKER]: HITL state hook write failed: {e}\n")

    def start_brokerage_loop(self):
        sys.stderr.write("⚡ Platform Broker Bridge Initialized.\n")
        
        while True:
            sock = self.connect_to_core()
            if not sock:
                time.sleep(3.0)
                continue

            buffer = ""
            try:
                while True:
                    # Check the operator state files for changes
                    self.check_for_operator_intervention(sock)

                    ready = select.select([sock], [], [], 0.5)
                    if ready[0]:
                        data = sock.recv(1024).decode()
                        if not data:
                            sys.stderr.write("🔌 [BROKER]: Core socket link severed.\n")
                            break
                        
                        buffer += data
                        while "\n" in buffer:
                            line, buffer = buffer.split("\n", 1)
                            if line.strip():
                                try:
                                    frame = json.loads(line.strip())
                                    self.dispatch_to_platform(frame)
                                    self.dispatch_to_hitl_telemetry(frame)
                                    print(f"📡 [BROKER]: Telemetry frame routed successfully at {frame.get('timestamp')}")
                                except Exception as parse_error:
                                    sys.stderr.write(f"⚠️ [BROKER]: Parsing exception: {parse_error}\n")
            except KeyboardInterrupt:
                sys.stderr.write("\n💤 Broker suspended.\n")
                break
            except Exception as loop_error:
                sys.stderr.write(f"⚠️ [BROKER]: Core link loop error: {loop_error}\n")
            finally:
                sock.close()
                time.sleep(2.0)

if __name__ == "__main__":
    broker = PlatformBroker()
    broker.start_brokerage_loop()
