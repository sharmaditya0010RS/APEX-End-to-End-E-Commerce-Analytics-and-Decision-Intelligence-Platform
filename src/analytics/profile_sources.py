from pathlib import Path
import json
import hashlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
QUALITY = ROOT / "reports" / "quality"
EDA = ROOT / "reports" / "eda"
MANIFEST = ROOT / "config" / "expected_sources.txt"

QUALITY.mkdir(parents=True, exist_ok=True)
EDA.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="deep")

files = [x.strip() for x in MANIFEST.read_text(encoding="utf-8-sig").splitlines() if x.strip()]

tables = {}
table_results = []
column_results = []
duplicate_results = []
fingerprints = []

for filename in files:
    path = RAW / filename
    if not path.is_file():
        raise FileNotFoundError(path)

    frame = pd.read_csv(path, low_memory=False)
    name = path.stem
    tables[name] = frame

    digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()

    fingerprints.append({
        "table": name,
        "file": filename,
        "sha256": digest
    })

    table_results.append({
        "table": name,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "file_bytes": int(path.stat().st_size),
        "memory_mb": round(frame.memory_usage(deep=True).sum() / 1048576, 3),
        "missing_cells": int(frame.isna().sum().sum()),
        "duplicate_rows": int(frame.duplicated().sum())
    })

    for column in frame.columns:
        values = frame[column]
        column_results.append({
            "table": name,
            "column": column,
            "dtype": str(values.dtype),
            "rows": int(len(frame)),
            "missing_count": int(values.isna().sum()),
            "missing_pct": round(float(values.isna().mean() * 100), 4),
            "unique_values": int(values.nunique(dropna=True)),
            "sample_value": str(values.dropna().iloc[0])[:120] if values.notna().any() else ""
        })

    duplicate_results.append({
        "table": name,
        "exact_duplicate_rows": int(frame.duplicated().sum())
    })

profile = pd.DataFrame(table_results)
columns = pd.DataFrame(column_results)
duplicates = pd.DataFrame(duplicate_results)

relationships = [
    ("olist_orders_dataset", "customer_id", "olist_customers_dataset", "customer_id"),
    ("olist_order_items_dataset", "order_id", "olist_orders_dataset", "order_id"),
    ("olist_order_items_dataset", "product_id", "olist_products_dataset", "product_id"),
    ("olist_order_items_dataset", "seller_id", "olist_sellers_dataset", "seller_id"),
    ("olist_order_payments_dataset", "order_id", "olist_orders_dataset", "order_id"),
    ("olist_order_reviews_dataset", "order_id", "olist_orders_dataset", "order_id")
]

relationship_results = []

for child_name, child_key, parent_name, parent_key in relationships:
    child = tables[child_name]
    parent = tables[parent_name]

    if child_key not in child.columns or parent_key not in parent.columns:
        raise ValueError(f"Missing relationship key: {child_name}.{child_key} -> {parent_name}.{parent_key}")

    parent_values = set(parent[parent_key].dropna().unique())
    child_values = child[child_key]

    unmatched = child_values.notna() & ~child_values.isin(parent_values)

    relationship_results.append({
        "child_table": child_name,
        "child_key": child_key,
        "parent_table": parent_name,
        "parent_key": parent_key,
        "child_rows": int(len(child)),
        "null_child_keys": int(child_values.isna().sum()),
        "orphan_rows": int(unmatched.sum()),
        "orphan_pct": round(float(unmatched.mean() * 100), 4),
        "parent_duplicate_keys": int(parent[parent_key].duplicated().sum())
    })

relations = pd.DataFrame(relationship_results)

expected_keys = [
    ("olist_orders_dataset", "order_id"),
    ("olist_customers_dataset", "customer_id"),
    ("olist_products_dataset", "product_id"),
    ("olist_sellers_dataset", "seller_id")
]

key_results = []

for table_name, key in expected_keys:
    frame = tables[table_name]
    key_results.append({
        "table": table_name,
        "key": key,
        "null_keys": int(frame[key].isna().sum()),
        "duplicate_keys": int(frame[key].duplicated().sum()),
        "unique_nonnull_keys": int(frame[key].nunique(dropna=True))
    })

keys = pd.DataFrame(key_results)

profile.to_csv(QUALITY / "table_profile.csv", index=False)
columns.to_csv(QUALITY / "column_profile.csv", index=False)
duplicates.to_csv(QUALITY / "duplicates.csv", index=False)
relations.to_csv(QUALITY / "relationships.csv", index=False)
keys.to_csv(QUALITY / "primary_key_checks.csv", index=False)
pd.DataFrame(fingerprints).to_csv(QUALITY / "source_hashes.csv", index=False)

plt.figure(figsize=(13, 6))
sns.barplot(data=profile.sort_values("rows"), x="rows", y="table")
plt.title("Source Table Row Counts")
plt.xlabel("Rows")
plt.ylabel("")
plt.tight_layout()
plt.savefig(EDA / "01_source_table_sizes.png", dpi=180)
plt.close()

missing = columns[columns["missing_count"] > 0].sort_values("missing_pct", ascending=False).head(30)

plt.figure(figsize=(13, max(5, len(missing) * 0.35)))
if not missing.empty:
    missing = missing.copy()
    missing["field"] = missing["table"].str.replace("olist_", "", regex=False) + " / " + missing["column"]
    sns.barplot(data=missing, x="missing_pct", y="field")
else:
    plt.text(0.5, 0.5, "No missing values found", ha="center", va="center")
plt.title("Top Missing-Value Percentages")
plt.xlabel("Missing %")
plt.ylabel("")
plt.tight_layout()
plt.savefig(EDA / "02_missing_values.png", dpi=180)
plt.close()

orders = tables["olist_orders_dataset"].copy()
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
monthly = (
    orders.dropna(subset=["order_purchase_timestamp"])
    .assign(month=lambda d: d["order_purchase_timestamp"].dt.to_period("M").dt.to_timestamp())
    .groupby("month")
    .size()
    .rename("orders")
    .reset_index()
)
monthly.to_csv(QUALITY / "monthly_order_coverage.csv", index=False)

plt.figure(figsize=(14, 5))
sns.lineplot(data=monthly, x="month", y="orders", marker="o")
plt.title("Historical Monthly Order Coverage")
plt.xlabel("Purchase Month")
plt.ylabel("Order Records")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(EDA / "03_monthly_orders.png", dpi=180)
plt.close()

status = orders["order_status"].fillna("MISSING").value_counts().reset_index()
status.columns = ["status", "orders"]
status.to_csv(QUALITY / "order_status_distribution.csv", index=False)

plt.figure(figsize=(11, 5))
sns.barplot(data=status, x="orders", y="status")
plt.title("Order Status Distribution")
plt.xlabel("Order Records")
plt.ylabel("")
plt.tight_layout()
plt.savefig(EDA / "04_order_status.png", dpi=180)
plt.close()

plt.figure(figsize=(12, 5))
sns.barplot(data=relations, x="orphan_rows", y="child_table")
plt.title("Referential Integrity: Orphan Rows")
plt.xlabel("Orphan Rows")
plt.ylabel("")
plt.tight_layout()
plt.savefig(EDA / "05_relationship_integrity.png", dpi=180)
plt.close()

summary = {
    "source_tables": len(tables),
    "total_rows_across_tables": int(profile["rows"].sum()),
    "total_columns_across_tables": int(profile["columns"].sum()),
    "total_missing_cells": int(profile["missing_cells"].sum()),
    "total_exact_duplicate_rows": int(profile["duplicate_rows"].sum()),
    "total_relationship_orphan_rows": int(relations["orphan_rows"].sum()),
    "visuals_generated": 5,
    "data_source": "Original Olist CSV files",
    "dataset_period": "Historical",
    "status": "Profiled, not cleaned or modeled"
}

(QUALITY / "profile_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

print(json.dumps(summary, indent=2))
print("\nPRIMARY KEY CHECKS")
print(keys.to_string(index=False))
print("\nRELATIONSHIP CHECKS")
print(relations.to_string(index=False))
print("\nSOURCE PROFILING COMPLETED")
