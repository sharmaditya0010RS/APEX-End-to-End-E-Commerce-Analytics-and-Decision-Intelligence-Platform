from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

root = Path(__file__).resolve().parents[2]
raw = root / "data" / "raw"
quality = root / "reports" / "quality"
charts = root / "reports" / "eda"

quality.mkdir(parents=True, exist_ok=True)
charts.mkdir(parents=True, exist_ok=True)

manifest = [
    name.strip()
    for name in (root / "config" / "expected_sources.txt").read_text(encoding="utf-8-sig").splitlines()
    if name.strip()
]

frames = {}
duplicates = []
missing = []

for filename in manifest:
    frame = pd.read_csv(raw / filename, low_memory=False)
    name = Path(filename).stem
    frames[name] = frame

    duplicates.append({
        "table": name,
        "rows": len(frame),
        "exact_duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_pct": round(100 * frame.duplicated().mean(), 4),
        "unique_rows": int(len(frame.drop_duplicates()))
    })

    for column in frame.columns:
        count = int(frame[column].isna().sum())
        missing.append({
            "table": name,
            "column": column,
            "missing_count": count,
            "missing_pct": round(100 * count / len(frame), 4)
        })

duplicate_df = pd.DataFrame(duplicates)
missing_df = pd.DataFrame(missing)

duplicate_df.to_csv(quality / "duplicate_investigation.csv", index=False)
missing_df.to_csv(quality / "missingness_investigation.csv", index=False)

sns.set_theme(style="whitegrid")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=duplicate_df.sort_values("exact_duplicate_rows"), x="exact_duplicate_rows", y="table", ax=ax)
ax.set_title("Exact Duplicate Rows by Source Table")
ax.set_xlabel("Duplicate Rows")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(charts / "11_duplicate_concentration.png", dpi=200)
plt.close(fig)

top_missing = missing_df.sort_values("missing_count", ascending=False).head(20).copy()
top_missing["field"] = top_missing["table"] + " | " + top_missing["column"]

fig, ax = plt.subplots(figsize=(14, 8))
sns.barplot(data=top_missing, x="missing_count", y="field", ax=ax)
ax.set_title("Top 20 Fields by Missing-Value Count")
ax.set_xlabel("Missing Cells")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(charts / "12_missingness_concentration.png", dpi=200)
plt.close(fig)

orders = frames["olist_orders_dataset"]
date_columns = [
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

status_missing = (
    orders.groupby("order_status", dropna=False)[date_columns]
    .apply(lambda x: x.isna().mean() * 100)
)

status_missing.to_csv(quality / "order_status_missingness.csv")

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(status_missing, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax)
ax.set_title("Missing Date Fields by Order Status (%)")
ax.set_xlabel("")
ax.set_ylabel("Order Status")
fig.tight_layout()
fig.savefig(charts / "13_status_missingness_heatmap.png", dpi=200)
plt.close(fig)

geo = frames["olist_geolocation_dataset"]

geo_summary = {
    "geolocation_rows": int(len(geo)),
    "exact_duplicate_rows": int(geo.duplicated().sum()),
    "distinct_zip_prefixes": int(geo["geolocation_zip_code_prefix"].nunique()),
    "zip_prefixes_with_multiple_records": int(
        geo.groupby("geolocation_zip_code_prefix").size().gt(1).sum()
    )
}

pd.DataFrame([geo_summary]).to_csv(quality / "geolocation_investigation.csv", index=False)

products = frames["olist_products_dataset"]
categories = frames["product_category_name_translation"]

unmapped = products.loc[
    products["product_category_name"].notna()
    & ~products["product_category_name"].isin(categories["product_category_name"])
]

coverage = pd.DataFrame([
    {
        "check": "Orders without payment records",
        "count": int((~orders["order_id"].isin(frames["olist_order_payments_dataset"]["order_id"])).sum())
    },
    {
        "check": "Orders without review records",
        "count": int((~orders["order_id"].isin(frames["olist_order_reviews_dataset"]["order_id"])).sum())
    },
    {
        "check": "Products with null categories",
        "count": int(products["product_category_name"].isna().sum())
    },
    {
        "check": "Products with unmapped nonnull categories",
        "count": int(len(unmapped))
    }
])

coverage.to_csv(quality / "business_coverage_checks.csv", index=False)

print("\nDUPLICATE INVESTIGATION")
print(duplicate_df.to_string(index=False))

print("\nTOP MISSING FIELDS")
print(missing_df.sort_values("missing_count", ascending=False).head(15).to_string(index=False))

print("\nORDER STATUS MISSINGNESS")
print(status_missing.round(2).to_string())

print("\nGEOLOCATION")
print(pd.DataFrame([geo_summary]).to_string(index=False))

print("\nBUSINESS COVERAGE")
print(coverage.to_string(index=False))

print("\nDEEP QUALITY INVESTIGATION COMPLETED")
