from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs" / "decision" / "evidence"

CAPACITIES = (1, 5, 10, 20, 50, 100)
EFFECTIVENESS = (0.10, 0.25, 0.50)
COSTS = (2, 5, 10)
VALUES = (20, 50, 100)


def decision_evidence():
    scenarios = pd.read_csv(EVIDENCE / "phase07_decision_scenarios.csv")
    break_even = pd.read_csv(EVIDENCE / "phase07_break_even_summary.csv")
    manifest = json.loads(
        (EVIDENCE / "phase07_decision_scenario_manifest.json")
        .read_text(encoding="utf-8-sig")
    )

    if len(scenarios) != 162 or len(break_even) != 6:
        raise ValueError("Phase 7 record counts do not reconcile")

    if manifest.get("validation") != "PASS":
        raise ValueError("Phase 7 evidence is not validated")

    if manifest.get("realized_savings_claim") is not False:
        raise ValueError("Realized savings must not be claimed")

    if manifest.get("intervention_effectiveness_observed") is not False:
        raise ValueError("Effectiveness must remain hypothetical")

    if manifest.get("scenario_count") != 162:
        raise ValueError("Manifest scenario count mismatch")

    keys = [
        "review_budget_pct",
        "assumed_intervention_effectiveness",
        "assumed_review_cost_brl",
        "assumed_value_per_prevented_late_brl"
    ]

    if scenarios[keys].duplicated().any():
        raise ValueError("Scenario dimension combination duplicated")

    if not np.allclose(
        scenarios["scenario_review_expense_brl"],
        scenarios["orders_reviewed"] * scenarios["assumed_review_cost_brl"]
    ):
        raise ValueError("Review expense formula mismatch")

    expected_model_net = (
        scenarios["observed_model_late_identified"]
        * scenarios["assumed_intervention_effectiveness"]
        * scenarios["assumed_value_per_prevented_late_brl"]
        - scenarios["scenario_review_expense_brl"]
    )

    expected_random_net = (
        scenarios["random_expected_late_identified"]
        * scenarios["assumed_intervention_effectiveness"]
        * scenarios["assumed_value_per_prevented_late_brl"]
        - scenarios["scenario_review_expense_brl"]
    )

    if not np.allclose(scenarios["model_scenario_net_brl"], expected_model_net):
        raise ValueError("Model scenario arithmetic mismatch")

    if not np.allclose(scenarios["random_scenario_net_brl"], expected_random_net):
        raise ValueError("Random scenario arithmetic mismatch")

    if not np.allclose(
        scenarios["model_incremental_vs_random_brl"],
        expected_model_net - expected_random_net
    ):
        raise ValueError("Incremental comparison mismatch")

    if break_even["financially_viable_under_assumptions"].astype(str).str.lower().eq("true").any():
        raise ValueError("Reference-case no-go conclusion changed")

    for column, expected in [
        ("review_budget_pct", CAPACITIES),
        ("assumed_intervention_effectiveness", EFFECTIVENESS),
        ("assumed_review_cost_brl", COSTS),
        ("assumed_value_per_prevented_late_brl", VALUES)
    ]:
        if not np.allclose(sorted(scenarios[column].unique()), expected):
            raise ValueError(f"Unexpected levels for {column}")

    return {
        "scenarios": scenarios,
        "break_even": break_even,
        "manifest": manifest
    }


def selected_scenario(data, capacity, effectiveness, cost, value):
    capacity = int(capacity)
    effectiveness = float(effectiveness)
    cost = float(cost)
    value = float(value)

    if (
        capacity not in CAPACITIES
        or effectiveness not in EFFECTIVENESS
        or cost not in COSTS
        or value not in VALUES
    ):
        raise ValueError("Selection outside documented scenario grid")

    frame = data["scenarios"]
    match = frame.loc[
        np.isclose(frame["review_budget_pct"], capacity)
        & np.isclose(frame["assumed_intervention_effectiveness"], effectiveness)
        & np.isclose(frame["assumed_review_cost_brl"], cost)
        & np.isclose(frame["assumed_value_per_prevented_late_brl"], value)
    ]

    if len(match) != 1:
        raise ValueError("Exactly one documented scenario must match")

    return match.iloc[0]
