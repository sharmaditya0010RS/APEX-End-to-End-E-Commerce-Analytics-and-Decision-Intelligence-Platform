from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

root = Path(__file__).resolve().parents[2]
out = root / "reports" / "eda" / "phase05"
out.mkdir(parents=True, exist_ok=True)
load_dotenv(root / ".env")

with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    options="-c max_parallel_workers_per_gather=0 -c work_mem=16MB"
) as conn:
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT
                cohort_month,
                months_since_first,
                observed_activity_pct
            FROM analytics.v_customer_cohort_matrix
            ORDER BY cohort_month, months_since_first
        """)
        cohort_rows = cursor.fetchall()

        cursor.execute("""
            SELECT customer_segment, customers, gross_item_value
            FROM analytics.v_customer_segment_summary
            ORDER BY gross_item_value DESC
        """)
        segment_rows = cursor.fetchall()

cohorts = pd.DataFrame(
    cohort_rows,
    columns=["cohort_month", "month", "activity_pct"]
)

segments = pd.DataFrame(
    segment_rows,
    columns=["segment", "customers", "gross_item_value"]
)

cohorts["activity_pct"] = pd.to_numeric(cohorts["activity_pct"])
segments["gross_item_value"] = pd.to_numeric(segments["gross_item_value"])

matrix = cohorts.pivot(
    index="cohort_month",
    columns="month",
    values="activity_pct"
)

matrix.index = pd.to_datetime(matrix.index).strftime("%Y-%m")

fig, ax = plt.subplots(figsize=(16, 10))

sns.heatmap(
    matrix,
    mask=matrix.isna(),
    cmap="YlGnBu",
    linewidths=0.4,
    linecolor="#dddddd",
    cbar_kws={"label": "Observed monthly repeat activity (%)"},
    ax=ax
)

ax.set_title("Customer Cohort Activity — 0% vs Unobservable Months")
ax.set_xlabel("Months Since First Delivered Purchase")
ax.set_ylabel("Acquisition Cohort")
fig.tight_layout()
fig.savefig(out / "34_cohort_activity_heatmap.png", dpi=200)
plt.close(fig)

fig, ax = plt.subplots(figsize=(12, 6))
plot_data = segments.sort_values("gross_item_value")

sns.barplot(
    data=plot_data,
    x="gross_item_value",
    y="segment",
    ax=ax
)

ax.set_xlabel("Delivered Gross Item Value (BRL)")
ax.set_ylabel("")
ax.set_title("Observed Delivered Item Value by Customer Segment")
fig.tight_layout()
fig.savefig(out / "35_customer_segment_value.png", dpi=200)
plt.close(fig)

matrix.to_csv(out / "cohort_activity_matrix.csv")
segments.to_csv(out / "customer_segment_summary.csv", index=False)

print("COHORT MATRIX ROWS:", len(cohorts))
print("CUSTOMER SEGMENTS:", len(segments))
print("TRUE ZERO CELLS:", int(matrix.eq(0).sum().sum()))
print("UNOBSERVABLE CELLS:", int(matrix.isna().sum().sum()))
print("PHASE 5 CUSTOMER VISUALS GENERATED")
