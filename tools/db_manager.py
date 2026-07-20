#!/usr/bin/env python3
# db_manager.py — Centralized SQLite WAL Database Orchestrator (v1.3.0)
import os
import sqlite3
import time
import json

class ManifoldDatabase:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.db_path = os.path.join(self.repo_dir, "cognitive_history.db")
        self.initialize_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def initialize_db(self):
        os.makedirs(self.repo_dir, exist_ok=True)
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trajectories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                gain REAL NOT NULL,
                dampening REAL NOT NULL,
                trust_level TEXT NOT NULL,
                active_mode TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS safety_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT NOT NULL,
                resolved INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attractor_nodes (
                label TEXT PRIMARY KEY,
                x REAL NOT NULL,
                y REAL NOT NULL,
                z REAL NOT NULL,
                weight REAL DEFAULT 1.0,
                decay REAL DEFAULT 0.01,
                last_updated REAL NOT NULL
            )
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_traj_time ON trajectories(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_safety_time ON safety_events(timestamp)")

        conn.commit()
        conn.close()

    def log_trajectory(self, x: float, y: float, z: float, gain: float, damp: float, trust: str, mode: str):
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO trajectories (timestamp, x, y, z, gain, dampening, trust_level, active_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (time.time(), x, y, z, gain, damp, trust, mode))
        conn.commit()
        conn.close()

    def log_safety_event(self, event_type: str, details: dict):
        conn = self.get_connection()
        conn.execute("""
            INSERT INTO safety_events (timestamp, event_type, details)
            VALUES (?, ?, ?)
        """, (time.time(), event_type, json.dumps(details)))
        conn.commit()
        conn.close()

    def get_recent_trajectory_window(self, limit: int = 10) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, x, y, z, gain, dampening, trust_level, active_mode 
            FROM trajectories 
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "time": round(r[0], 2), "coords": [round(r[1], 3), round(r[2], 3), round(r[3], 3)],
                "gain": r[4], "damp": r[5], "trust": r[6], "mode": r[7]
            } for r in rows
        ]

    def get_recent_safety_events(self, limit: int = 5) -> list:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, event_type, details, resolved 
            FROM safety_events 
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "time": round(r[0], 2), "event": r[1],
                "details": json.loads(r[2]) if r[2] else {}, "resolved": bool(r[3])
            } for r in rows
        ]

    def reconstruct_incident_episode(self, seconds_ago: int = 60) -> dict:
        """Assembles a compact temporal summary of system dynamics during a disruption."""
        start_time = time.time() - seconds_ago
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Pull anomalies in this window
        cursor.execute("SELECT timestamp, event_type FROM safety_events WHERE timestamp >= ? ORDER BY timestamp ASC", (start_time,))
        events = [{"t_offset": round(time.time() - r[0], 1), "type": r[1]} for r in cursor.fetchall()]
        
        # Compute trajectory vector velocity trends to save context bytes
        cursor.execute("SELECT x, y, z FROM trajectories WHERE timestamp >= ? ORDER BY timestamp ASC", (start_time,))
        coords = cursor.fetchall()
        conn.close()
        
        if not coords:
            return {"span_reviewed_sec": seconds_ago, "events_found": events, "motion_trend": "STATIC"}
            
        # Extract starting vs ending coordinate divergence
        first, last = coords[0], coords[-1]
        delta_x = abs(last[0] - first[0])
        delta_y = abs(last[1] - first[1])
        delta_z = abs(last[2] - first[2])
        
        return {
            "span_reviewed_sec": seconds_ago,
            "events_found": events,
            "net_displacement": [round(delta_x, 2), round(delta_y, 2), round(delta_z, 2)],
            "data_points_analyzed": len(coords)
        }

if __name__ == "__main__":
    db = ManifoldDatabase()
    print("💾 SQLite WAL Engine upgraded with Episode Tracking functions.")
