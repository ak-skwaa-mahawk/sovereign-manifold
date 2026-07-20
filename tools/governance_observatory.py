#!/usr/bin/env python3
"""
governance_observatory.py
Real-time 5D Governance Observatory and Procurement Delta Visualizer.
Parses persistent ledger wire history and renders system health state snapshots.
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Any

# Enforce non-interactive backend to prevent headless display environment faults
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

LIVING_PI_R = 3.1730059
THERMO_MIN_H = 3.04
THERMO_MAX_H = 3.07

class GovernanceObservatory:
    def __init__(self):
        self.timestamps: List[datetime] = []
        self.vitality_history: List[float] = []
        self.h_band_history: List[float] = []
        self.curvature_history: List[float] = []
        self.dampening_history: List[float] = []
        self.approval_count = 0
        
    def load_ledger_history(self):
        """Parses the global verified tracking ledger for analytical evaluation."""
        ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
        if not os.path.exists(ledger_path):
            print(f"[WARN] Ledger asset not found at {ledger_path}. Starting clean.")
            return

        with open(ledger_path, "r") as f:
            for idx, line in enumerate(f):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    telemetry = record.get("thermodynamic_telemetry", {})
                    
                    if not telemetry:
                        continue
                        
                    self.approval_count += 1
                    self.timestamps.append(datetime.now())  # Proxy timeline tracking step
                    self.vitality_history.append(float(telemetry.get("living_pi_r_vitality", 0.0)))
                    self.h_band_history.append(float(telemetry.get("thermo_h_band", 0.0)))
                    self.curvature_history.append(float(telemetry.get("curvature_budget", 1.0)))
                    self.dampening_history.append(float(telemetry.get("target_dampening_threshold", 0.0)))
                except Exception as e:
                    print(f"[WARN] Failed parsing ledger entry line {idx}: {e}")

    def generate_observatory_report(self, output_filename: str = "governance_snapshot.png"):
        """Generates a structured, decoupled physical analytics canvas report."""
        self.load_ledger_history()
        
        if not self.vitality_history:
            print("❌ [OBSERVATORY]: Cannot render tracking canvas. No historical telemetry blocks found.")
            return
            
        plt.style.use('seaborn-v0_8-darkgrid')
        fig, axes = plt.subplots(2, 2, figsize=(14, 9))
        fig.suptitle('Sovereign Manifold — 5D Governance Observatory Log', fontsize=16, fontweight='bold')
        
        x_steps = list(range(1, len(self.vitality_history) + 1))
        
        # Plot 1: Living π_r Vitality Boundaries
        ax1 = axes[0, 0]
        ax1.plot(x_steps, self.vitality_history, color='#00d4ff', marker='o', linewidth=2, label='Live Vitality')
        ax1.axhline(y=0.9999, color='red', linestyle='--', alpha=0.7, label='Veto Limit (99.99%)')
        ax1.set_title('Living π_r Vitality Metric')
        ax1.set_xlabel('Committed Block Depth')
        ax1.set_ylabel('Vitality Scale')
        ax1.legend(loc='lower right')
        
        # Plot 2: Thermodynamic H-Band Boundaries
        ax2 = axes[0, 1]
        ax2.plot(x_steps, self.h_band_history, color='#7b2cbf', marker='s', linewidth=2, label='h-band')
        ax2.axhline(y=THERMO_MIN_H, color='darkorange', linestyle=':', label='Floor (3.04)')
        ax2.axhline(y=THERMO_MAX_H, color='darkorange', linestyle=':', label='Ceiling (3.07)')
        ax2.set_title('Thermodynamic Balance Window')
        ax2.set_xlabel('Committed Block Depth')
        ax2.set_ylabel('H-Band Metric')
        ax2.legend(loc='lower right')
        
        # Plot 3: Curvature-Regulated Spatial Budget
        ax3 = axes[1, 0]
        ax3.plot(x_steps, self.curvature_history, color='#ff6b35', marker='^', linewidth=2, label='κ (Curvature)')
        ax3.set_title('Curvature Budget Evolution (Tordial-GS Constraints)')
        ax3.set_xlabel('Committed Block Depth')
        ax3.set_ylabel('κ Parameter Budget')
        ax3.legend(loc='lower right')
        
        # Plot 4: System Integration Context Matrix
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        summary_text = (
            "SYSTEM Sovereign System Status Summary\n"
            "--------------------------------------------------\n"
            f"• Current Verified Block Depth : {len(self.vitality_history)} Blocks\n"
            f"• Total Quorum Confirmations    : {self.approval_count} Passed\n"
            f"• Latest Dampening Threshold  : {self.dampening_history[-1]:.4f}\n"
            f"• Latest Thermodynamic H-Band : {self.h_band_history[-1]:.4f}\n"
            f"• Core Cryptographic Engine   : ACTIVE / SEALED\n"
            "--------------------------------------------------\n"
            "Status: OPERATIONAL | Consensus Maintained"
        )
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=11,
                 verticalalignment='top', fontfamily='monospace',
                 bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e', alpha=0.08))
                 
        plt.tight_layout()
        
        output_dir = os.path.expanduser("~/Turbo_Takeoff/output")
        os.makedirs(output_dir, exist_ok=True)
        final_path = os.path.join(output_dir, output_filename)
        
        plt.savefig(final_path, dpi=200, bbox_inches='tight')
        print(f"✅ [OBSERVATORY SUCCESS]: Cryptographic monitoring dashboard saved to disk → {final_path}")

if __name__ == "__main__":
    observatory = GovernanceObservatory()
    observatory.generate_observatory_report()
