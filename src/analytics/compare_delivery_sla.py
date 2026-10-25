from pathlib import Path
import pandas as pd

root = Path(__file__).resolve().parents[2]
orders = pd.read_csv(root / "data" / "raw" / "olist_orders_dataset.csv")

actual = pd.to_datetime(
    orders["order_delivered_customer_date"],
    errors="coerce"
)

estimated = pd.to_datetime(
    orders["order_estimated_delivery_date"],
    errors="coerce"
)

eligible = (
    orders["order_status"].eq("delivered")
    & actual.notna()
    & estimated.notna()
)

timestamp_late = actual[eligible] > estimated[eligible]

calendar_late = (
    actual[eligible].dt.normalize()
    > estimated[eligible].dt.normalize()
)

result = pd.DataFrame([
    {
        "definition": "Timestamp",
        "eligible_orders": int(eligible.sum()),
        "late_orders": int(timestamp_late.sum()),
        "late_pct": round(timestamp_late.mean() * 100, 4)
    },
    {
        "definition": "Calendar Date",
        "eligible_orders": int(eligible.sum()),
        "late_orders": int(calendar_late.sum()),
        "late_pct": round(calendar_late.mean() * 100, 4)
    }
])

result.to_csv(
    root / "reports" / "quality" / "sla_definition_comparison.csv",
    index=False
)

print(result.to_string(index=False))
