from pathlib import Path
import json

import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
out = root / "reports" / "decision"

data = pd.read_csv(out / "phase07_decision_scenarios.csv")
manifest = json.loads(
    (out / "phase07_decision_scenario_manifest.json").read_text(
        encoding="utf-8"
    )
)

checks = {}

checks["scenario_count"] = len(data) == 162
checks["unique_scenario_combinations"] = not data.duplicated(
    subset=[
        "review_budget_pct",
        "assumed_intervention_effectiveness",
        "assumed_review_cost_brl",
        "assumed_value_per_prevented_late_brl"
    ]
).any()

expected_cost = (
    data["orders_reviewed"] * data["assumed_review_cost_brl"]
)

checks["review_cost_reconciliation"] = np.allclose(
    data["scenario_review_expense_brl"],
    expected_cost
)

expected_model = (
    data["observed_model_late_identified"]
    * data["assumed_intervention_effectiveness"]
    * data["assumed_value_per_prevented_late_brl"]
    - expected_cost
)

checks["model_value_reconciliation"] = np.allclose(
    data["model_scenario_net_brl"],
    expected_model
)

expected_random = (
    data["random_expected_late_identified"]
    * data["assumed_intervention_effectiveness"]
    * data["assumed_value_per_prevented_late_brl"]
    - expected_cost
)

checks["random_value_reconciliation"] = np.allclose(
    data["random_scenario_net_brl"],
    expected_random
)

checks["no_claimed_realized_savings"] = (
    manifest["realized_savings_claim"] is False
    and manifest["intervention_effectiveness_observed"] is False
)

checks["original_model_unchanged"] = (
    manifest["model_retrained"] is False
    and manifest["test_threshold_retuned"] is False
)

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if not all(checks.values()):
    raise RuntimeError("Decision intelligence validation failed")

print("PHASE 7 SCENARIO VALIDATION: 7/7 PASS")
