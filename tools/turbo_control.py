#!/usr/bin/env python3
# turbo_control.py — Operator CLI and Telemetry Viewer for Turbo_Takeoff (v2.2.0)
import os
import sys
import json
import socket
import argparse
import select

class TurboControlCLI:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.socket_path = os.path.join(self.repo_dir, "run/control.sock")

    def connect_socket(self) -> socket.socket:
        if not os.path.exists(self.socket_path):
            print("❌ [SOCKET ERROR]: Control socket not found at run/control.sock")
            print("   Make sure the autopilot daemon is running.")
            sys.exit(1)
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            return sock
        except Exception as e:
            print(f"❌ [CONNECTION ERROR]: Failed to connect to socket: {e}")
            sys.exit(1)

    def send_command(self, cmd_payload: dict):
        """Dispatches a structured JSON command over the socket and awaits acknowledgment."""
        sock = self.connect_socket()
        try:
            # Send serialized command with newline framing
            sock.sendall((json.dumps(cmd_payload) + "\n").encode())
            
            ready = select.select([sock], [], [], 1.5)
            if ready[0]:
                response = sock.recv(2048).decode().strip()
                print("\n🛰️  [SYSTEM RESPONSE]:")
                for line in response.split('\n'):
                    try:
                        parsed = json.loads(line)
                        print(json.dumps(parsed, indent=2))
                    except:
                        print(f"   {line}")
            else:
                print("⚠️  Command sent, but no response received within timeout.")
        finally:
            sock.close()

    def run_live_monitor(self):
        sock = self.connect_socket()
        print("⚡ Operator telemetry link established. Waiting for state stream...")
        
        buffer = ""
        try:
            while True:
                ready = select.select([sock], [], [])
                if ready[0]:
                    data = sock.recv(1024).decode()
                    if not data:
                        print("\n🔌 Connection severed by host daemon.")
                        break
                    
                    buffer += data
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if line.strip():
                            self.render_telemetry_frame(line.strip())
        except KeyboardInterrupt:
            print("\n💤 Telemetry link closed safely.")
        finally:
            sock.close()

    def render_telemetry_frame(self, raw_json: str):
        try:
            frame = json.loads(raw_json)
        except json.JSONDecodeError:
            return

        ts = frame.get("timestamp", "")
        event = frame.get("event", "UNKNOWN")
        status = frame.get("status", {})
        trust = frame.get("system_trust_level", "UNKNOWN")
        limits = frame.get("dynamic_limits", {})

        os.system("clear")
        print("=" * 64)
        print("🦅  TURBO_TAKEOFF OPERATOR MONITOR [Active Link]")
        print("=" * 64)
        print(f"⏱️  Telemetry Time : {ts}")
        print(f"🏷️  Current Event  : {event}")
        print(f"🛡️  Trust Rating   : {trust}")
        print("-" * 64)
        print("📊 METRIC VARIABLES:")
        print(f"   -> System Gain          : {status.get('gain', 0.0):.4f}")
        print(f"   -> Modulation Offset    : {status.get('modulation_hz', 0.0):.4f} Hz")
        print(f"   -> Dampening Coefficient: {status.get('dampening', 0.0):.4f}")
        print("-" * 64)
        print("🧠 ADAPTATION METRICS:")
        print(f"   -> Control Openness (%) : {limits.get('active_scale', 0.0) * 100.0:.2f} %")
        print(f"   -> Effective Gain Slew  : {limits.get('active_gain_slew', 0.0):.4f}")
        print("=" * 64)
        print("Press Ctrl+C to disconnect monitor link...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Turbo_Takeoff operator control utility.")
    
    # Mutually exclusive main actions
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--monitor", action="store_true", help="Launch live telemetry display.")
    action_group.add_argument("--takeover", action="store_true", help="Assert manual operator control override.")
    action_group.add_argument("--release", action="store_true", help="Relinquish manual control back to autonomous loop.")
    action_group.add_argument("--send", type=str, help="Inject a raw legacy string command.")

    # Override tuning parameters
    parser.add_argument("--gain", type=float, help="Override target system gain.")
    parser.add_argument("--damp", type=float, help="Override target system dampening coefficient.")
    parser.add_argument("-y", "--yes", action="store_true", help="Bypass takeover safety confirmation prompts.")

    args = parser.parse_args()
    cli = TurboControlCLI()

    if args.monitor:
        cli.run_live_monitor()
    elif args.release:
        cmd = {"command": "RELEASE"}
        cli.send_command(cmd)
    elif args.send:
        cmd = {"command": "RAW", "payload": args.send.upper()}
        cli.send_command(cmd)
    elif args.takeover:
        if not args.yes:
            confirm = input("⚠️  WARNING: Assert manual control override over active flight loop? [y/N]: ")
            if confirm.lower() not in ["y", "yes"]:
                print("❌ Manual takeover aborted by operator.")
                sys.exit(0)
        
        cmd = {
            "command": "OVERRIDE",
            "parameters": {
                "gain": args.gain if args.gain is not None else 1.5000,
                "dampening": args.damp if args.damp is not None else 0.3000
            }
        }
        cli.send_command(cmd)
