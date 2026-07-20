#!/usr/bin/env python3
# test_agent.py — Expanded Agent Simulator for Tordial Memory & Diagnostics (v1.1.0)
import os
import sys
import json
import subprocess
import time

class LocalTordialAgent:
    def __init__(self):
        self.mcp_script = os.path.expanduser("~/Turbo_Takeoff/tools/tordial_mcp_server.py")

    def call_mcp(self, method: str, params: dict = None) -> dict:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        proc = subprocess.Popen(
            [sys.executable, self.mcp_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, _ = proc.communicate(input=json.dumps(request) + "\n")
        try:
            return json.loads(stdout.strip())
        except Exception as e:
            return {"error": f"Failed to parse MCP output: {e}", "raw": stdout}

    def run_simulation(self):
        print("🤖 [LOCAL AGENT]: Commencing expanded flight diagnostics & memory verification...")
        time.sleep(1.0)

        # 1. Query the expanded tool listings
        print("\n🔍 Step 1: Discovering updated MCP Tools...")
        tools = self.call_mcp("tools/list")
        for tool in tools.get("result", {}).get("tools", []):
            print(f"   -> Found Tool: {tool['name']}")
        time.sleep(1.0)

        # 2. Access learned spatial memory (Attractor nodes)
        print("\n💾 Step 2: Querying learned spatial coordination nodes...")
        nodes = self.call_mcp("tools/call", {"name": "get_attractor_nodes"})
        print(f"   -> Node Memory Database:\n{nodes.get('result', {}).get('content', [{}])[0].get('text', '{}')}")
        time.sleep(1.0)

        # 3. Assess trajectory drift and momentum
        print("\n📈 Step 3: Evaluating coordinate drift and system coherence...")
        traj = self.call_mcp("tools/call", {"name": "get_trajectory_summary"})
        print(f"   -> Trajectory Report:\n{traj.get('result', {}).get('content', [{}])[0].get('text', '{}')}")
        time.sleep(1.0)

        # 4. Inject a new attractor memory target coordinate
        print("\n🧠 Step 4: Injecting a new target calibration attractor...")
        injection = self.call_mcp("tools/call", {
            "name": "force_create_node",
            "arguments": {"label": "recovery_sector_nine", "x": 3.1415, "y": -1.5707, "z": 9.8066}
        })
        print(f"   -> Database Log:\n{injection.get('result', {}).get('content', [{}])[0].get('text', '{}')}")
        time.sleep(1.0)

        # 5. Re-query nodes to verify memory permanence
        print("\n💾 Step 5: Re-evaluating database to confirm memory permanence...")
        nodes_updated = self.call_mcp("tools/call", {"name": "get_attractor_nodes"})
        print(f"   -> Updated Node Database:\n{nodes_updated.get('result', {}).get('content', [{}])[0].get('text', '{}')}")
        
        print("\n🏆 Verification flight complete. The cognitive gateway is fully loaded.")

if __name__ == "__main__":
    agent = LocalTordialAgent()
    agent.run_simulation()
