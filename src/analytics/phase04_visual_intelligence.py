from pathlib import Path
import json
import os

import numpy as np
import pandas as pd
import psycopg
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "eda" / "phase04"
QUALITY = ROOT / "reports" / "quality"
OUT.mkdir(parents=True, exist_ok=True)
QUALITY.mkdir(parents=True, exist_ok=True)
load_dotenv(ROOT / ".env")

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams["figure.figsize"] = (12, 6)

def fetch(query):
    with psycopg.connect(
        host="127.0.0.1",
        port=5433,
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            names = [x.name for x in cur.description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=names)

def save(name, title):
    plt.title(title)
    plt.tight_layout()
    plt.savefig(OUT / f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close()

orders = fetch("SELECT * FROM analytics.v_order_intelligence")
sellers = fetch("SELECT * FROM analytics.v_seller_intelligence")
customers = fetch("SELECT * FROM analytics.v_customer_intelligence")

orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])
orders["purchase_month"] = pd.to_datetime(orders["purchase_month"])
orders["gross_item_value"] = pd.to_numeric(orders["gross_item_value"])
orders["freight_value"] = pd.to_numeric(orders["freight_value"])
orders["average_review_score"] = pd.to_numeric(orders["average_review_score"])
orders["delivery_difference_days"] = pd.to_numeric(orders["delivery_difference_days"])
sellers["seller_item_value"] = pd.to_numeric(sellers["seller_item_value"])
customers["observed_item_value"] = pd.to_numeric(customers["observed_item_value"])

monthly = orders.groupby("purchase_month").agg(
    orders=("order_id", "nunique"),
    item_value=("gross_item_value", "sum")
).reset_index()
monthly["aov"] = monthly["item_value"] / monthly["orders"]

status = orders["order_status"].value_counts()
regions = orders.groupby("customer_state").agg(
    orders=("order_id", "nunique"),
    item_value=("gross_item_value", "sum")
).sort_values("item_value", ascending=False)
region_late = orders.loc[orders["delivery_sla_eligible"]].groupby("customer_state").agg(
    eligible=("order_id", "count"),
    late=("is_late_calendar", "sum")
)
region_late["late_pct"] = 100 * region_late["late"] / region_late["eligible"]

sellers["delivery_sla_eligible"] = sellers["delivery_sla_eligible"].eq(True)
sellers["is_late_calendar"] = sellers["is_late_calendar"].eq(True)

seller_summary = sellers.groupby("seller_id").agg(
    orders=("order_id", "nunique"),
    item_value=("seller_item_value", "sum"),
    eligible=("delivery_sla_eligible", "sum"),
    late=("is_late_calendar", "sum")
)

seller_summary["late_pct"] = np.nan

eligible_sellers = seller_summary["eligible"] >= 30

seller_summary.loc[eligible_sellers, "late_pct"] = (
    seller_summary.loc[eligible_sellers, "late"].astype(float)
    / seller_summary.loc[eligible_sellers, "eligible"].astype(float)
    * 100
)

plt.figure()
plt.plot(monthly["purchase_month"], monthly["orders"], marker="o")
save("14_monthly_orders", "Monthly Marketplace Order Volume")

plt.figure()
plt.plot(monthly["purchase_month"], monthly["item_value"], marker="o")
save("15_monthly_item_value", "Monthly Gross Item Value (BRL)")

plt.figure()
plt.plot(monthly["purchase_month"], monthly["aov"], marker="o")
save("16_monthly_aov", "Average Gross Item Value per Order")

plt.figure()
sns.barplot(x=status.values, y=status.index)
save("17_order_status", "Marketplace Order Status Distribution")

plt.figure()
regions.head(15)["item_value"].sort_values().plot.barh()
plt.xlabel("Gross Item Value (BRL)")
save("18_top_states", "Top Customer States by Gross Item Value")

plt.figure()
regions.head(15)["orders"].sort_values().plot.barh()
plt.xlabel("Orders")
save("19_state_order_volume", "Top Customer States by Order Volume")

plt.figure()
sns.histplot(orders["gross_item_value"].dropna(), bins=70)
save("20_order_value_distribution", "Gross Item Value per Order")

plt.figure()
sns.histplot(orders["gross_item_value"].dropna().clip(upper=1000), bins=60)
save("21_order_value_zoom", "Order Item Value Distribution: Capped View")

plt.figure()
sns.histplot(orders["freight_value"].dropna().clip(upper=200), bins=60)
save("22_freight_distribution", "Freight Value per Order: Capped View")

plt.figure()
sns.histplot(customers["lifetime_order_count"], discrete=True)
plt.xlim(0, min(15, customers["lifetime_order_count"].max()))
save("23_customer_frequency", "Observed Orders per Unique Customer")

plt.figure()
sns.histplot(customers["observed_item_value"].dropna().clip(upper=1000), bins=60)
save("24_customer_value", "Observed Customer Item Value: Capped View")

cohorts = customers["acquisition_cohort"].value_counts().sort_index()
plt.figure()
cohorts.plot(kind="bar", width=0.8)
plt.xlabel("First Purchase Cohort")
plt.xticks(rotation=70)
save("25_customer_cohorts", "Customer Acquisition Cohort Sizes")

plt.figure()
sns.histplot(seller_summary["orders"], bins=60)
plt.xscale("symlog")
save("26_seller_order_concentration", "Seller Order Volume Distribution")

plt.figure()
sns.scatterplot(
    data=seller_summary,
    x="orders",
    y="item_value",
    alpha=0.4
)
plt.xscale("symlog")
plt.yscale("symlog")
save("27_seller_volume_value", "Seller Order Count vs Item Value")

plt.figure()
valid_sellers = seller_summary.loc[seller_summary["eligible"] >= 30]
sns.scatterplot(data=valid_sellers, x="eligible", y="late_pct", alpha=0.5)
plt.xscale("log")
save("28_seller_delivery_risk", "Seller Late Delivery Rate (30+ Eligible Orders)")

plt.figure()
region_late.loc[region_late["eligible"] >= 100, "late_pct"].sort_values().plot.barh()
plt.xlabel("Calendar-Date Late Delivery Rate (%)")
save("29_regional_lateness", "Regional Late Delivery Rates (100+ Eligible Orders)")

plt.figure()
sns.histplot(
    orders.loc[orders["delivery_sla_eligible"], "delivery_difference_days"].dropna().clip(-60, 60),
    bins=70
)
plt.axvline(0, linestyle="--", color="red")
save("30_delivery_difference", "Delivery Time vs Estimated Timestamp")

plt.figure()
sns.boxplot(
    data=orders.loc[
        orders["delivery_sla_eligible"]
        & orders["average_review_score"].notna()
    ].assign(
        delivery_group=lambda d: np.where(d["is_late_calendar"], "Late", "On time")
    ),
    x="delivery_group",
    y="average_review_score"
)
save("31_reviews_by_delivery", "Review Scores by Delivery SLA Classification")

plt.figure()
sns.histplot(orders["average_review_score"].dropna(), bins=20)
save("32_order_review_distribution", "Order-Level Average Review Score Distribution")

plt.figure()
seller_summary["item_value"].sort_values(ascending=False).head(20).sort_values().plot.barh()
plt.xlabel("Gross Item Value (BRL)")
save("33_top_sellers", "Top 20 Sellers by Gross Item Value")

summary = {
    "order_records": int(len(orders)),
    "distinct_customers": int(len(customers)),
    "seller_order_records": int(len(sellers)),
    "figures_created": len(list(OUT.glob("*.png"))),
    "gross_item_value_brl": float(orders["gross_item_value"].sum()),
    "delivered_orders": int(orders["order_status"].eq("delivered").sum()),
    "sla_eligible": int(orders["delivery_sla_eligible"].sum()),
    "late_calendar_orders": int(orders["is_late_calendar"].fillna(False).sum())
}

(QUALITY / "phase04_analytics_summary.json").write_text(
    json.dumps(summary, indent=2),
    encoding="utf-8"
)

monthly.to_csv(QUALITY / "phase04_monthly_commercial.csv", index=False)
regions.to_csv(QUALITY / "phase04_regional_commercial.csv")
seller_summary.to_csv(QUALITY / "phase04_seller_summary.csv")

print(json.dumps(summary, indent=2))
print("PHASE 4 VISUAL ANALYTICS GENERATED")
