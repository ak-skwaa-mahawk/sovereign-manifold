#!/usr/bin/env python3
"""
takeoff_resonance.py
Target Calculation Engine for dynamic raw material weight adjustment.
Integrates regional supply condition signals with the 5D council gate.
"""

import os
import sys
import json
import hashlib
from typing import Dict, Any, List, Optional

# Ensure internal modules resolve when executed directly or externally
sys.path.append(os.path.expanduser('~/Turbo_Takeoff/tools'))
import council_orchestrator

LIVING_PI_R = 3.1730059

def calculate_ethical_resonance(supplier: Dict[str, Any]) -> float:
    """Calculates the absolute Ethical Resonance Score (0-100)."""
    comp_score = 100.0 if supplier.get("compliance_certified", False) else 40.0
    ownership_score = 100.0 if supplier.get("sovereign_ownership", False) else 50.0
    community_score = float(supplier.get("community_standing_rating", 75))
    
    raw_resonance = (comp_score * 0.35) + (ownership_score * 0.35) + (community_score * 0.30)
    return round(max(0.0, min(100.0, raw_resonance)), 2)

def process_takeoff_manifest() -> Dict[str, Any]:
    """Retains legacy processing metrics for backwards-compatibility loops."""
    materials_takeoff = [
        {"item": "Reinforced Concrete Foundation", "quantity": "450 CUYD", "base_cost": 54000.0},
        {"item": "Structural Timber Framework (ANCSA Leased Lumber)", "quantity": "12,500 BDFT", "base_cost": 18750.0},
        {"item": "Insulated Sheathing Paneling", "quantity": "3,200 SQFT", "base_cost": 9600.0}
    ]
    
    suppliers_db = {
        "Yukon Outpost Logistics": {"compliance_certified": True, "sovereign_ownership": True, "community_standing_rating": 95},
        "Standard Bulk Procurement Corp": {"compliance_certified": True, "sovereign_ownership": False, "community_standing_rating": 70}
    }
    
    evaluated_takeoffs = []
    total_project_cost = 0.0
    
    for material in materials_takeoff:
        selected_supplier = "Standard Bulk Procurement Corp"
        if "Timber" in material["item"] or "ANCSA" in material["item"]:
            selected_supplier = "Yukon Outpost Logistics"
            
        supplier_data = suppliers_db[selected_supplier]
        resonance_score = calculate_ethical_resonance(supplier_data)
        total_project_cost += material["base_cost"]
        
        evaluated_takeoffs.append({
            "material": material["item"],
            "qty": material["quantity"],
            "allocated_supplier": selected_supplier,
            "ethical_resonance_score": resonance_score,
            "line_cost": material["base_cost"]
        })
        
    return {
        "project_takeoff_summary": evaluated_takeoffs,
        "aggregate_metrics": {
            "total_estimated_cost": total_project_cost,
            "mean_ethical_resonance": round(sum(t["ethical_resonance_score"] for t in evaluated_takeoffs) / len(evaluated_takeoffs), 2)
        }
    }

def load_regional_supply_signal(region: str = "default") -> Dict[str, float]:
    """Fetches availability and pricing signals for the target geographic coordinates."""
    signals = {
        "default": {"availability": 0.92, "price_volatility": 0.18, "resonance_bonus": 0.07},
        "alaska_interior": {"availability": 0.78, "price_volatility": 0.31, "resonance_bonus": 0.12},
        "yukon_flats": {"availability": 0.65, "price_volatility": 0.27, "resonance_bonus": 0.15},
    }
    res = dict(signals.get(region, signals["default"]))
    res["region"] = region
    return res

def calculate_resonance_weight_adjustment(
    current_quantities: Dict[str, float],
    supply_signal: Dict[str, float],
    current_state: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Computes weight deltas and filters updates through the council gate."""
    if current_state is None:
        current_state = council_orchestrator.fetch_daemon_state()

    adjustments = {}
    for material, qty in current_quantities.items():
        resonance_factor = 1.0 + supply_signal.get("resonance_bonus", 0.0)
        volatility_penalty = 1.0 - (supply_signal.get("price_volatility", 0.2) * 0.6)
        availability_boost = supply_signal.get("availability", 0.9) ** 0.7

        raw_adjust = (resonance_factor * availability_boost / volatility_penalty) - 1.0
        # Prevent wild scaling steps; ensure adjustments damp smoothly near the bounds
        proposed_delta = round(raw_adjust * 0.004, 4) if current_state.get("target_dampening_threshold", 0.61) > 0.62 else round(raw_adjust * 0.005, 4)

        adjustments[material] = {
            "current_qty": qty,
            "proposed_delta": proposed_delta,
            "proposed_new_qty": round(qty * (1 + proposed_delta), 2),
        }

    # Format localized changes into canonical 5D matrix updates
    mean_delta = sum(a["proposed_delta"] for a in adjustments.values()) / len(adjustments)
    council_deltas = {
        "surplus_threshold": round(mean_delta * 0.2, 4),
        "target_dampening": round(mean_delta * 0.1, 4),
        "curvature_budget": -0.01 if supply_signal.get("price_volatility", 0) > 0.25 else 0.00,
    }

    # Intercept changes using the 5D Council Pre-Screener
    council_result = council_orchestrator.simulate_5d_agent_debate(council_deltas, current_state)

    if council_result is None:
        return {
            "status": "VETOED_BY_5D_COUNCIL",
            "reason": "Proposed material weight adjustments violated structural manifold boundaries.",
        }

    # Append valid updates into the global tracking log
    ledger_path = os.path.expanduser("~/Turbo_Takeoff/public_ledger_wire.jsonl")
    try:
        with open(ledger_path, "a") as f:
            f.write(json.dumps(council_result) + "\n")
    except Exception as e:
        return {"status": "ERROR_WRITE_FAILED", "reason": str(e)}

    return {
        "status": "APPROVED_AND_ANCHORED",
        "quantity_adjustments": adjustments,
        "sha256": council_result["cryptographic_anchor"]["bound_parameters_manifest_sha256"],
    }

if __name__ == "__main__":
    # Test harness simulating local regional takeoff modifications
    test_takeoff = {
        "waterproofing_membrane": 1240.0,
        "insulation_board": 890.5,
        "sealant_cartridges": 156.0,
    }
    
    signal = load_regional_supply_signal("alaska_interior")
    result = calculate_resonance_weight_adjustment(test_takeoff, signal)
    
    print("\n🚀 --- [ADAPTIVE TARGET ENGINE VERDICT] ---")
    print(json.dumps(result, indent=4))
