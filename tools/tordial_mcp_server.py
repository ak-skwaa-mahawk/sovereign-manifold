#!/usr/bin/env python3
# tordial_mcp_server.py — Multi-Horizon Adaptive Interface (v3.2.0)
import os
import sys
import json
import socket
import select
import sqlite3
import time

class TordialMCPServer:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.socket_path = os.path.join(self.repo_dir, "run/control.sock")
        self.db_path = os.path.join(self.repo_dir, "cognitive_history.db")
        self.master_db_path = os.path.join(self.repo_dir, "master_timeline.db")
        self.ledger_path = os.path.join(self.repo_dir, "public_ledger_wire.jsonl")

    def query_daemon(self, cmd_dict: dict = None) -> dict:
        if not os.path.exists(self.socket_path):
            return {"error": "Daemon control socket offline."}
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.socket_path)
            sock.setblocking(False)
            select.select([sock], [], [], 0.1)
            if cmd_dict:
                sock.sendall((json.dumps(cmd_dict) + "\n").encode())
            else:
                sock.sendall(b'{"command": "RAW", "payload": "STATUS_QUERY"}\n')
            ready = select.select([sock], [], [], 0.5)
            if ready[0]:
                response = sock.recv(4096).decode().strip()
                for line in reversed(response.split('\n')):
                    if line.strip():
                        return json.loads(line.strip())
            return {"error": "Timeout waiting for daemon response."}
        except Exception as e:
            return {"error": f"Socket IPC failure: {str(e)}"}
        finally:
            sock.close()

    def get_surplus_vector(self, window_seconds: int = 60) -> dict:
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cutoff_time = time.time() - window_seconds
            cursor.execute("""
                SELECT timestamp, x_est, y_est, z_est, v_magnitude, uncertainty
                FROM predictions WHERE timestamp >= ? ORDER BY id DESC LIMIT 15
            """, (cutoff_time,))
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 2:
                return {"status": "DORMANT_RESERVOIR", "residual_energy": 0.0, "vector_trend": "STABLE"}
                
            first_v = rows[-1][4] if rows[-1][4] is not None else 0.0
            last_v = rows[0][4] if rows[0][4] is not None else 0.0
            v_delta = last_v - first_v
            
            trend = "STABLE"
            if v_delta > 0.02: trend = "ACCELERATING_SURPLUS"
            elif v_delta < -0.02: trend = "DECAYING_SURPLUS"
            
            return {
                "status": "HORIZON_SEED_ACTIVE",
                "residual_energy_magnitude": round(last_v, 4),
                "net_velocity_delta": round(v_delta, 4),
                "vector_trend": trend,
                "loop_return_velocity_mean": round(last_v, 4),
                "current_uncertainty": round(rows[0][5], 4) if rows[0][5] else 0.0
            }
        except Exception as e:
            return {"error": f"Surplus vector extraction failure: {str(e)}"}

    def get_master_timeline_summary(self, lookback_seconds: int = 3600) -> dict:
        if not os.path.exists(self.master_db_path):
            return {"error": "Master timeline database not initialized yet."}
        try:
            conn = sqlite3.connect(self.master_db_path)
            cursor = conn.cursor()
            cutoff = time.time() - lookback_seconds

            cursor.execute("""
                SELECT COUNT(*), AVG(surplus_velocity), 
                       SUM(CASE WHEN active_trust = 'SIGMOID_CLAMPED' THEN 1 ELSE 0 END)
                FROM timeline_events WHERE block_timestamp >= ?
            """, (cutoff,))
            total, avg_v, clamp_count = cursor.fetchone()
            conn.close()

            return {
                "timeline_lookback_window_seconds": lookback_seconds,
                "total_historical_blocks_tracked": total,
                "macro_rolling_velocity_average": round(avg_v, 4) if avg_v else 0.0,
                "total_historical_clamp_interventions": clamp_count if clamp_count else 0
            }
        except Exception as e:
            return {"error": f"Timeline summary computation failure: {str(e)}"}

    def get_high_surplus_windows(self, min_velocity: float = 1.5) -> dict:
        if not os.path.exists(self.master_db_path):
            return {"error": "Master database offline."}
        try:
            conn = sqlite3.connect(self.master_db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT block_timestamp, active_trust, surplus_velocity, trend_direction, sig_proof 
                FROM timeline_events WHERE surplus_velocity >= ? ORDER BY block_timestamp ASC LIMIT 5
            """, (min_velocity,))
            rows = cursor.fetchall()
            conn.close()

            windows = []
            for row in rows:
                windows.append({
                    "event_time": row[0],
                    "trust_state": row[1],
                    "velocity_magnitude": row[2],
                    "trend_label": row[3],
                    "envelope_proof": row[4][:8] if row[4] else "NONE"
                })

            return {
                "query_threshold_limit": min_velocity,
                "total_isolated_anomaly_points": len(windows),
                "extracted_windows": windows
            }
        except Exception as e:
            return {"error": f"Anomaly slicing failure: {str(e)}"}

    def apply_adaptive_tuning(self, target_dampening: float, justification: str) -> dict:
        """Dispatches an agent-derived parameter recommendation directly to the daemon."""
        payload = {
            "command": "ADJUST_PARAMETERS",
            "target_dampening": target_dampening,
            "justification": justification
        }
        return self.query_daemon(payload)

    def export_ledger_segment(self, limit: int = 10) -> dict:
        if not os.path.exists(self.ledger_path):
            return {"error": "Ledger wire file missing."}
        try:
            blocks = []
            with open(self.ledger_path, "r") as f:
                for line in f:
                    if line.strip():
                        blocks.append(json.loads(line.strip()))
            segment = blocks[-limit:] if len(blocks) > limit else blocks
            return {
                "export_status": "VERIFIED_PORTABLE_PACKET",
                "checksum_horizon_blocks": len(segment),
                "payload_envelope": segment
            }
        except Exception as e:
            return {"error": f"Failed to build distribution envelope: {str(e)}"}

    def run(self):
        try:
            for line in sys.stdin:
                if not line.strip():
                    continue
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                req_id = request.get("id")
                method = request.get("method")
                params = request.get("params", {})

                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {"tools": {"listChanged": False}},
                            "serverInfo": {"name": "tordial-manifold-mcp", "version": "3.2.0"}
                        }
                    }
                elif method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {
                            "tools": [
                                {"name": "inspect_system_state", "description": "Fetch state.", "inputSchema": {"type": "object", "properties": {}}},
                                {"name": "get_surplus_vector", "description": "Get current remainder.", "inputSchema": {"type": "object", "properties": {}}},
                                {"name": "get_master_timeline_summary", "description": "Compute macro statistics.", "inputSchema": {"type": "object", "properties": {}}},
                                {"name": "get_high_surplus_windows", "description": "Isolate high variance windows.", "inputSchema": {"type": "object", "properties": {"min_velocity": {"type": "number"}}}},
                                {"name": "apply_adaptive_tuning", "description": "Submits historical-informed tracking updates to control loop.", "inputSchema": {"type": "object", "properties": {"target_dampening": {"type": "number"}, "justification": {"type": "string"}}, "required": ["target_dampening", "justification"]}},
                                {"name": "export_ledger_segment", "description": "Extract standalone packet.", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer"}}}}
                            ]
                        }
                    }
                elif method == "tools/call":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})

                    if tool_name == "inspect_system_state":
                        content = [{"type": "text", "text": json.dumps(self.query_daemon(), indent=2)}]
                    elif tool_name == "get_surplus_vector":
                        content = [{"type": "text", "text": json.dumps(self.get_surplus_vector(), indent=2)}]
                    elif tool_name == "get_master_timeline_summary":
                        content = [{"type": "text", "text": json.dumps(self.get_master_timeline_summary(), indent=2)}]
                    elif tool_name == "get_high_surplus_windows":
                        mv = float(tool_args.get("min_velocity", 1.5))
                        content = [{"type": "text", "text": json.dumps(self.get_high_surplus_windows(mv), indent=2)}]
                    elif tool_name == "apply_adaptive_tuning":
                        td = float(tool_args.get("target_dampening", 0.5))
                        just = str(tool_args.get("justification", "Agent tuning pass"))
                        content = [{"type": "text", "text": json.dumps(self.apply_adaptive_tuning(td, just), indent=2)}]
                    elif tool_name == "export_ledger_segment":
                        lim = int(tool_args.get("limit", 5))
                        content = [{"type": "text", "text": json.dumps(self.export_ledger_segment(lim), indent=2)}]
                    else:
                        content = [{"type": "text", "text": f"Error: Tool {tool_name} not found."}]

                    response = {
                        "jsonrpc": "2.0",
                        "id": req_id,
                        "result": {"content": content}
                    }
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    server = TordialMCPServer()
    server.run()
