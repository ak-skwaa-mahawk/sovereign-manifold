#!/usr/bin/env python3
"""
stress_test_compliance.py
Long-Term Compliance Variance & Soliton Stability Simulator.
Feeds macro-environmental shocks across a 36-month horizon into the 5D Council Gate.
"""

import os
import sys
import json
import random

sys.path.append(os.path.expanduser('~/Turbo_Takeoff/tools'))
import council_orchestrator

def run_multi_month_simulation(months: int = 36):
    print(f"🛠️  [SIMULATOR]: Initializing {months}-month macroeconomic structural stress test...")
    
    # Fetch base state to run standard projection against
    current_state = council_orchestrator.fetch_daemon_state()
    
    # Environmental shock profiles mapping to (surplus_threshold_delta, target_dampening_delta)
    shock_events = {
        "ANCSA_REGULATORY_SHIFT": (0.04, -0.01),
        "LABOR_SUPPLY_CONSTRAINT": (-0.03, 0.02),
        "EPA_COMPLIANCE_SHOCK": (0.01, -0.02),
        "EQUILIBRIUM_BASELINE": (0.00, 0.00)
    }
    
    historical_log = []
    veto_count = 0
    approved_count = 0
    
    print(f"📈 [SIMULATOR]: Injecting pseudo-randomized supply variance parameters...")
    print(f"| Month | Shock Event Type         | Vitality | H-Band  | Verdict   |")
    print(f"|-------|--------------------------|----------|---------|-----------|")
    
    for month in range(1, months + 1):
        # Determine current month's macro environment
        if month in [6, 18, 30]:
            event_name = "ANCSA_REGULATORY_SHIFT"
        elif month in [12, 24]:
            event_name = "LABOR_SUPPLY_CONSTRAINT"
        elif month in [9, 21, 33]:
            event_name = "EPA_COMPLIANCE_SHOCK"
        else:
            event_name = "EQUILIBRIUM_BASELINE"
            
        s_delta, d_delta = shock_events[event_name]
        
        # Add slight stochastic noise to simulate day-to-day transaction friction
        s_delta += round(random.uniform(-0.005, 0.005), 4)
        d_delta += round(random.uniform(-0.005, 0.005), 4)
        
        proposed_deltas = {
            "surplus_threshold": s_delta,
            "target_dampening": d_delta,
            "curvature_budget": round(random.uniform(-0.002, 0.002), 4)
        }
        
        # Capture stdout to prevent nested transcript prints from cluttering the table layout
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        try:
            payload = council_orchestrator.simulate_5d_agent_debate(proposed_deltas, current_state)
        finally:
            sys.stdout.close()
            sys.stdout = old_stdout
            
        if payload is None:
            veto_count += 1
            verdict_str = "VETOED"
            # Extract expected parameters manually to plot failed trajectories
            regulated = council_orchestrator.curvature_regulated_drift(current_state, proposed_deltas)
            v_metric = round((regulated["target_dampening_threshold"] / council_orchestrator.LIVING_PI_R) * 4.8, 4)
            h_metric = round(3.04 + (regulated["target_dampening_threshold"] - 0.58) * 0.5, 4)
        else:
            approved_count += 1
            verdict_str = "APPROVED"
            current_state = payload["thermodynamic_telemetry"]
            v_metric = current_state["living_pi_r_vitality"]
            h_metric = current_state["thermo_h_band"]
            
        print(f"| {str(month).zfill(2)}    | {event_name.ljust(24)} | {v_metric:.4f}   | {h_metric:.4f}  | {verdict_str.ljust(9)} |")
        
        historical_log.append({
            "month": month,
            "event": event_name,
            "vitality": v_metric,
            "h_band": h_metric,
            "verdict": verdict_str
        })
        
    print(f"\n📊 --- [SIMULATION RUN COMPLETION METRICS] ---")
    print(f"   • Total Simulated Windows   : {months} Months")
    print(f"   • Total State Optimizations : {approved_count} Passed")
    print(f"   • Total Safety Interventions: {veto_count} Shielded")
    print(f"   • System Survivability Rate : {round((approved_count / months) * 100, 2)}%")
    print("==============================================")

if __name__ == "__main__":
    run_multi_month_simulation(36)
