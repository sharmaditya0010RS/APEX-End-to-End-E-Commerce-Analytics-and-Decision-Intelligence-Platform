from pathlib import Path
import numpy as np
import pandas as pd

root = Path(__file__).resolve().parents[2]
out = root / "reports" / "decision"

data = pd.read_csv(out / "phase07_decision_scenarios.csv")
summary = pd.read_csv(out / "phase07_break_even_summary.csv")

checks = {}

checks["six_capacity_levels"] = len(summary) == 6

checks["no_duplicate_capacities"] = (
    summary["review_budget_pct"].is_unique
)

required = (
    summary["scenario_review_expense_brl"]
    / (summary["observed_model_late_identified"] * 0.25)
)

checks["break_even_formula"] = np.allclose(
    summary["break_even_prevention_value_brl"],
    required
)

checks["baseline_matches_scenario_grid"] = np.allclose(
    summary["model_scenario_net_brl"],
    data.loc[
        data["assumed_intervention_effectiveness"].eq(0.25)
        & data["assumed_review_cost_brl"].eq(5.0)
        & data["assumed_value_per_prevented_late_brl"].eq(50.0)
    ].sort_values("review_budget_pct")["model_scenario_net_brl"].to_numpy()
)

checks["viability_flag_correct"] = (
    summary["financially_viable_under_assumptions"].astype(str).str.lower()
    .eq(summary["model_scenario_net_brl"].ge(0).astype(str).str.lower())
).all()

checks["positive_break_even_values"] = (
    summary["break_even_prevention_value_brl"].gt(0).all()
)

figures = list((out / "figures").glob("phase07_*.png"))

checks["three_valid_figures"] = (
    len(figures) == 3
    and all(path.stat().st_size > 1000 for path in figures)
)

for name, passed in checks.items():
    print(f"{name}: {'PASS' if passed else 'FAIL'}")

if not all(checks.values()):
    raise RuntimeError("Phase 7 break-even validation failed")

print("PHASE 7 BREAK-EVEN VALIDATION: 7/7 PASS")
