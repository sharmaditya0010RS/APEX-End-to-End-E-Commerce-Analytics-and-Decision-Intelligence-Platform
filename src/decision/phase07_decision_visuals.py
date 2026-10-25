from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "decision"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

data = pd.read_csv(OUT / "phase07_decision_scenarios.csv")
manifest = json.loads(
    (OUT / "phase07_decision_scenario_manifest.json").read_text(encoding="utf-8")
)

if len(data) != 162 or manifest["scenario_count"] != 162:
    raise RuntimeError("Source scenarios do not reconcile")

base = data.loc[
    data["assumed_intervention_effectiveness"].eq(0.25)
    & data["assumed_review_cost_brl"].eq(5.0)
    & data["assumed_value_per_prevented_late_brl"].eq(50.0)
].sort_values("review_budget_pct").copy()

if len(base) != 6:
    raise RuntimeError("Baseline scenario count mismatch")

base["break_even_prevention_value_brl"] = (
    base["scenario_review_expense_brl"]
    / (
        base["observed_model_late_identified"]
        * base["assumed_intervention_effectiveness"]
    )
)

base["financially_viable_under_assumptions"] = (
    base["model_scenario_net_brl"] >= 0
)

base[[
    "review_budget_pct",
    "orders_reviewed",
    "observed_model_late_identified",
    "scenario_review_expense_brl",
    "break_even_prevention_value_brl",
    "model_scenario_net_brl",
    "financially_viable_under_assumptions"
]].to_csv(
    OUT / "phase07_break_even_summary.csv",
    index=False
)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(
    base["review_budget_pct"],
    base["break_even_prevention_value_brl"],
    marker="o"
)
ax.axhline(50, linestyle="--", label="Assumed BRL 50 value")
ax.set_xlabel("Orders Reviewed (%)")
ax.set_ylabel("Required Value per Prevented Late Order (BRL)")
ax.set_title("Break-Even Frontier at 25% Assumed Effectiveness")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "phase07_break_even_frontier.png", dpi=200)
plt.close(fig)

cost = data.loc[
    data["assumed_intervention_effectiveness"].eq(0.25)
    & data["assumed_value_per_prevented_late_brl"].eq(50.0)
    & data["review_budget_pct"].isin([1, 5, 10, 20])
].copy()

cost_pivot = cost.pivot(
    index="review_budget_pct",
    columns="assumed_review_cost_brl",
    values="model_scenario_net_brl"
)

fig, ax = plt.subplots(figsize=(10, 6))

for column in cost_pivot.columns:
    ax.plot(
        cost_pivot.index,
        cost_pivot[column],
        marker="o",
        label=f"Review cost: BRL {column:g}"
    )

ax.axhline(0, linestyle="--")
ax.set_xlabel("Orders Reviewed (%)")
ax.set_ylabel("Hypothetical Net Value (BRL)")
ax.set_title("Review Cost Sensitivity at 25% Effectiveness")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "phase07_cost_sensitivity.png", dpi=200)
plt.close(fig)

effect = data.loc[
    data["assumed_review_cost_brl"].eq(5.0)
    & data["assumed_value_per_prevented_late_brl"].eq(50.0)
    & data["review_budget_pct"].isin([1, 5, 10, 20])
].copy()

effect_pivot = effect.pivot(
    index="review_budget_pct",
    columns="assumed_intervention_effectiveness",
    values="model_scenario_net_brl"
)

fig, ax = plt.subplots(figsize=(10, 6))

for column in effect_pivot.columns:
    ax.plot(
        effect_pivot.index,
        effect_pivot[column],
        marker="o",
        label=f"Assumed effectiveness: {column:.0%}"
    )

ax.axhline(0, linestyle="--")
ax.set_xlabel("Orders Reviewed (%)")
ax.set_ylabel("Hypothetical Net Value (BRL)")
ax.set_title("Intervention Effectiveness Sensitivity")
ax.legend()
fig.tight_layout()
fig.savefig(FIG / "phase07_effectiveness_sensitivity.png", dpi=200)
plt.close(fig)

print("BREAK-EVEN FRONTIER")
print(base[[
    "review_budget_pct",
    "orders_reviewed",
    "observed_model_late_identified",
    "break_even_prevention_value_brl",
    "model_scenario_net_brl"
]].to_string(index=False, float_format=lambda value: f"{value:.2f}"))

print("DECISION VISUALS GENERATED: 3")
