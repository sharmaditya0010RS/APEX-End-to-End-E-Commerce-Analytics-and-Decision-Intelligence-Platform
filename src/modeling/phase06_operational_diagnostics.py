from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "modeling"
FIGURES = OUT / "figures"

data = pd.read_csv(
    OUT / "phase06_final_test_predictions.csv",
    parse_dates=["order_purchase_timestamp"]
)

results = json.loads(
    (OUT / "phase06_final_test_results.json").read_text(encoding="utf-8")
)

assert len(data) == 12507
assert data["order_id"].is_unique
assert data["target_late"].sum() == 601
assert data["predicted_late_probability"].between(0, 1).all()
assert data["predicted_late_probability"].notna().all()

data = data.sort_values(
    ["predicted_late_probability", "order_id"],
    ascending=[False, True]
).reset_index(drop=True)

population = len(data)
late_population = int(data["target_late"].sum())
base_rate = late_population / population

rows = []

for percentage in [1, 5, 10, 20, 50, 100]:
    reviewed = math.ceil(population * percentage / 100)
    selected = data.iloc[:reviewed]
    detected = int(selected["target_late"].sum())

    precision = detected / reviewed
    capture = detected / late_population
    lift = precision / base_rate

    rows.append({
        "review_budget_pct": percentage,
        "orders_reviewed": reviewed,
        "actual_late_detected": detected,
        "precision": precision,
        "late_capture_rate": capture,
        "lift_over_population": lift
    })

budget = pd.DataFrame(rows)

assert budget["actual_late_detected"].is_monotonic_increasing
assert budget["late_capture_rate"].between(0, 1).all()
assert budget["precision"].between(0, 1).all()
assert int(budget.iloc[-1]["actual_late_detected"]) == late_population
assert abs(budget.iloc[-1]["lift_over_population"] - 1) < 1e-10

budget.to_csv(
    OUT / "phase06_operational_review_budgets.csv",
    index=False
)

monthly = (
    data.assign(
        purchase_month=data["order_purchase_timestamp"].dt.strftime("%Y-%m")
    )
    .groupby("purchase_month")
    .agg(
        orders=("order_id", "count"),
        actual_late_rate=("target_late", "mean"),
        mean_predicted_risk=("predicted_late_probability", "mean")
    )
    .reset_index()
)

monthly.to_csv(
    OUT / "phase06_test_monthly_drift.csv",
    index=False
)

plt.figure(figsize=(10, 6))
plt.plot(
    budget["review_budget_pct"],
    budget["late_capture_rate"] * 100,
    marker="o",
    label="Model-ranked review"
)
plt.plot(
    [0, 100],
    [0, 100],
    linestyle="--",
    label="Random review expectation"
)
plt.xlabel("Percentage of Orders Reviewed")
plt.ylabel("Percentage of Late Orders Captured")
plt.title("Held-Out Test: Review Capacity vs Late-Order Capture")
plt.legend()
plt.tight_layout()
plt.savefig(
    FIGURES / "phase06_operational_capture.png",
    dpi=200
)
plt.close()

plt.figure(figsize=(9, 6))
x = np.arange(len(monthly))
width = 0.35

plt.bar(
    x - width / 2,
    monthly["actual_late_rate"] * 100,
    width,
    label="Actual late rate"
)
plt.bar(
    x + width / 2,
    monthly["mean_predicted_risk"] * 100,
    width,
    label="Mean predicted risk"
)
plt.xticks(x, monthly["purchase_month"])
plt.ylabel("Orders (%)")
plt.title("Held-Out Test: Monthly Prediction Drift")
plt.legend()
plt.tight_layout()
plt.savefig(
    FIGURES / "phase06_monthly_prediction_drift.png",
    dpi=200
)
plt.close()

summary = {
    "test_rows": population,
    "test_late_orders": late_population,
    "test_late_rate": base_rate,
    "selected_model": results["model"],
    "locked_threshold": results["locked_threshold"],
    "operational_budgets": rows,
    "monthly_drift": monthly.to_dict(orient="records"),
    "test_data_used_for_retraining": False,
    "test_data_used_for_threshold_selection": False,
    "financial_impact_estimated": False
}

(OUT / "phase06_operational_diagnostics.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

print(budget.to_string(index=False))
print()
print(monthly.to_string(index=False))
print()
print("OPERATIONAL DIAGNOSTICS VALIDATED")
