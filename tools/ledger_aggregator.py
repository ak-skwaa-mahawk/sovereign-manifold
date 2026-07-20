#!/usr/bin/env python3
# ledger_aggregator.py — Sovereign Timeline Aggregator Core (v1.0.0)
import os
import sys
import json
import sqlite3
import time

class LedgerTimelineAggregator:
    def __init__(self):
        self.repo_dir = os.path.expanduser("~/Turbo_Takeoff")
        self.db_path = os.path.join(self.repo_dir, "master_timeline.db")
        self.export_file = os.path.expanduser("~/Turbo_Takeoff/vhitzee_export_packet.json")
        self._init_database()

    def _init_database(self):
        """Creates the master indexed timeline schema for long-horizon forensic tracking."""
        conn = sqlite3.connect(self.db_path)
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS timeline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    block_timestamp REAL UNIQUE,
                    active_trust TEXT,
                    surplus_velocity REAL,
                    trend_direction TEXT,
                    sig_proof TEXT,
                    verification_anchor TEXT,
                    ingest_timestamp REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_ts ON timeline_events(block_timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timeline_trust ON timeline_events(active_trust)")
        conn.close()

    def ingest_export_packet(self) -> dict:
        """Ingests the distributed JSON transport packet, parses blocks, and aggregates metrics."""
        if not os.path.exists(self.export_file):
            return {"status": "NO_NEW_EXPORT_PACKET_FOUND", "records_added": 0}

        try:
            with open(self.export_file, "r") as f:
                packet = json.load(f)

            if packet.get("export_status") != "VERIFIED_PORTABLE_PACKET":
                return {"status": "INVALID_PACKET_SCHEMA", "records_added": 0}

            envelope = packet.get("payload_envelope", [])
            records_added = 0
            skipped_duplicates = 0

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for block in envelope:
                block_ts = block.get("timestamp")
                anchor = block.get("public_verification_anchor")
                sig_proof = block.get("signature_hash_proof")
                data_payload = block.get("data", {})

                # Extract nested data states smoothly
                trust = data_payload.get("active_trust", "UNKNOWN")
                surplus_v = data_payload.get("residual_surplus_velocity", 
                                             data_payload.get("vhitzee_surplus_ms", 0.0))
                trend = data_payload.get("trend_direction", "STABLE")

                try:
                    cursor.execute("""
                        INSERT INTO timeline_events 
                        (block_timestamp, active_trust, surplus_velocity, trend_direction, sig_proof, verification_anchor, ingest_timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (block_ts, trust, surplus_v, trend, sig_proof, anchor, time.time()))
                    records_added += 1
                except sqlite3.IntegrityError:
                    skipped_duplicates += 1

            conn.commit()
            conn.close()

            return {
                "status": "INGEST_COMPLETE",
                "records_added": records_added,
                "skipped_duplicates": skipped_duplicates,
                "master_db_path": self.db_path
            }

        except Exception as e:
            return {"status": "INGEST_FAILURE", "error": str(e)}

if __name__ == "__main__":
    aggregator = LedgerTimelineAggregator()
    result = aggregator.ingest_export_packet()
    print(json.dumps(result, indent=2))
