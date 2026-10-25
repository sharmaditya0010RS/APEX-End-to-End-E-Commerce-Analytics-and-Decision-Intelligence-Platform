from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "reports" / "eda"
QUALITY = ROOT / "reports" / "quality"

OUT.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

items = pd.read_csv(RAW / "olist_order_items_dataset.csv")
payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
orders = pd.read_csv(RAW / "olist_orders_dataset.csv")

metrics = []

for name, frame, column in [
    ("Item Price", items, "price"),
    ("Freight Value", items, "freight_value"),
    ("Payment Value", payments, "payment_value")
]:
    values = pd.to_numeric(frame[column], errors="coerce").dropna()

    metrics.append({
        "metric": name,
        "count": int(len(values)),
        "mean": float(values.mean()),
        "median": float(values.median()),
        "p95": float(values.quantile(0.95)),
        "p99": float(values.quantile(0.99)),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "negative_values": int((values < 0).sum())
    })

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(values, bins=60, ax=axes[0])
    axes[0].set_title(f"{name}: Full Distribution")
    sns.boxplot(x=values, ax=axes[1])
    axes[1].set_title(f"{name}: Outlier Overview")
    fig.tight_layout()
    fig.savefig(OUT / f"06_{name.lower().replace(' ', '_')}.png", dpi=180)
    plt.close(fig)

review_counts = reviews["review_score"].value_counts().sort_index()

plt.figure(figsize=(9, 5))
sns.barplot(x=review_counts.index.astype(str), y=review_counts.values)
plt.title("Customer Review Score Distribution")
plt.xlabel("Review Score")
plt.ylabel("Review Records")
plt.tight_layout()
plt.savefig(OUT / "09_review_scores.png", dpi=180)
plt.close()

for column in ["order_delivered_customer_date", "order_estimated_delivery_date"]:
    orders[column] = pd.to_datetime(orders[column], errors="coerce")

eligible = orders.loc[
    orders["order_status"].eq("delivered")
    & orders["order_delivered_customer_date"].notna()
    & orders["order_estimated_delivery_date"].notna()
].copy()

eligible["difference_days"] = (
    eligible["order_delivered_customer_date"]
    - eligible["order_estimated_delivery_date"]
).dt.total_seconds() / 86400

eligible["late"] = eligible["difference_days"] > 0

plt.figure(figsize=(12, 5))
sns.histplot(eligible["difference_days"].clip(-60, 60), bins=70)
plt.axvline(0, color="red", linestyle="--")
plt.title("Delivery Difference: Actual Minus Estimated")
plt.xlabel("Days: Negative = Early, Positive = Late")
plt.ylabel("Delivered Orders")
plt.tight_layout()
plt.savefig(OUT / "10_delivery_difference.png", dpi=180)
plt.close()

delivery_summary = pd.DataFrame([{
    "eligible_delivered_orders": len(eligible),
    "late_orders": int(eligible["late"].sum()),
    "late_rate_pct": round(100 * eligible["late"].mean(), 3) if len(eligible) else None,
    "median_difference_days": float(eligible["difference_days"].median()) if len(eligible) else None
}])

pd.DataFrame(metrics).to_csv(QUALITY / "numeric_distributions.csv", index=False)
delivery_summary.to_csv(QUALITY / "delivery_exploration.csv", index=False)

print("\nNUMERIC METRICS")
print(pd.DataFrame(metrics).to_string(index=False))
print("\nDELIVERY EXPLORATION")
print(delivery_summary.to_string(index=False))
print("\nADDITIONAL VISUAL ANALYSIS COMPLETED")
