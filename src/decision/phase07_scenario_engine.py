from pathlib import Path
from itertools import product
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "reports" / "modeling"
OUT = ROOT / "reports" / "decision"
OUT.mkdir(parents=True, exist_ok=True)

budget = pd.read_csv(SOURCE / "phase06_operational_review_budgets.csv")
test = json.loads(
    (SOURCE / "phase06_final_test_results.json").read_text(encoding="utf-8")
)

required = {
    "review_budget_pct",
    "orders_reviewed",
    "actual_late_detected"
}

if not required.issubset(budget.columns):
    raise RuntimeError("Operational budget columns missing")

if len(budget) != 6:
    raise RuntimeError("Expected six verified review capacities")

if int(test["test_rows"]) != 12507:
    raise RuntimeError("Unexpected test population")

if int(test["test_late_orders"]) != 601:
    raise RuntimeError("Unexpected observed late-order count")

if budget["review_budget_pct"].duplicated().any():
    raise RuntimeError("Duplicate review-capacity scenarios")

if int(budget.loc[
    budget["review_budget_pct"].eq(100),
    "actual_late_detected"
].iloc[0]) != 601:
    raise RuntimeError("Full-capacity reconciliation failed")

population = int(test["test_rows"])
late_population = int(test["test_late_orders"])
prevalence = late_population / population

effectiveness_values = [0.10, 0.25, 0.50]
review_cost_values = [2.0, 5.0, 10.0]
prevention_value_values = [20.0, 50.0, 100.0]

records = []

for _, item in budget.iterrows():
    capacity = float(item["review_budget_pct"])
    reviewed = int(item["orders_reviewed"])
    detected = int(item["actual_late_detected"])
    random_expected = reviewed * prevalence

    for effectiveness, review_cost, prevention_value in product(
        effectiveness_values,
        review_cost_values,
        prevention_value_values
    ):
        review_expense = reviewed * review_cost

        model_gross_value = detected * effectiveness * prevention_value
        random_gross_value = random_expected * effectiveness * prevention_value

        records.append({
            "review_budget_pct": capacity,
            "orders_reviewed": reviewed,
            "observed_model_late_identified": detected,
            "random_expected_late_identified": random_expected,
            "assumed_intervention_effectiveness": effectiveness,
            "assumed_review_cost_brl": review_cost,
            "assumed_value_per_prevented_late_brl": prevention_value,
            "scenario_review_expense_brl": review_expense,
            "model_scenario_net_brl": model_gross_value - review_expense,
            "random_scenario_net_brl": random_gross_value - review_expense,
            "model_incremental_vs_random_brl": (
                model_gross_value - random_gross_value
            ),
            "break_even_value_per_prevention_brl": (
                review_expense / (detected * effectiveness)
                if detected > 0 and effectiveness > 0
                else np.nan
            )
        })

scenarios = pd.DataFrame(records)

if len(scenarios) != 162:
    raise RuntimeError("Expected 162 scenario combinations")

if not np.isfinite(
    scenarios["model_scenario_net_brl"].to_numpy()
).all():
    raise RuntimeError("Nonfinite model scenario result")

zero_effect_check = (
    scenarios["model_scenario_net_brl"]
    <= scenarios["observed_model_late_identified"]
    * scenarios["assumed_intervention_effectiveness"]
    * scenarios["assumed_value_per_prevented_late_brl"]
).all()

if not zero_effect_check:
    raise RuntimeError("Scenario economics identity failed")

scenarios.to_csv(
    OUT / "phase07_decision_scenarios.csv",
    index=False
)

summary = {
    "phase": 7,
    "validation": "PASS",
    "scenario_count": int(len(scenarios)),
    "capacity_levels": sorted(
        scenarios["review_budget_pct"].unique().tolist()
    ),
    "effectiveness_assumptions": effectiveness_values,
    "review_cost_assumptions_brl": review_cost_values,
    "prevention_value_assumptions_brl": prevention_value_values,
    "test_orders": population,
    "observed_test_late_orders": late_population,
    "realized_savings_claim": False,
    "intervention_effectiveness_observed": False,
    "random_baseline_type": "expected_value",
    "model_retrained": False,
    "test_threshold_retuned": False
}

(OUT / "phase07_decision_scenario_manifest.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

selected = scenarios.loc[
    scenarios["review_budget_pct"].isin([1, 5, 10, 20])
    & scenarios["assumed_intervention_effectiveness"].eq(0.25)
    & scenarios["assumed_review_cost_brl"].eq(5.0)
    & scenarios["assumed_value_per_prevented_late_brl"].eq(50.0)
]

print("ILLUSTRATIVE ASSUMPTIONS ONLY")
print("Effectiveness: 25%")
print("Review cost: BRL 5 per order")
print("Value per prevention: BRL 50")
print()
print(selected[
    [
        "review_budget_pct",
        "orders_reviewed",
        "observed_model_late_identified",
        "model_scenario_net_brl",
        "random_scenario_net_brl",
        "model_incremental_vs_random_brl"
    ]
].to_string(index=False))

print()
print("TOTAL SCENARIOS:", len(scenarios))
print("PHASE 7 DECISION SCENARIO ENGINE VALIDATED")
