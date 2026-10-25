from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / "src" / "dashboard"))

from data_access import customer_intelligence_data

data = customer_intelligence_data()

segments = data["segments"]
cohorts = data["cohorts"]

assert len(segments) == 6
assert sum(row["customers"] for row in segments) == 93358
assert sum(row["orders"] for row in segments) == 96478
assert abs(
    sum(row["gross_value"] for row in segments) - 13221498.11
) < 0.02

assert len(cohorts) == 299
assert sum(row["observable"] for row in cohorts) == 208
assert sum(not row["observable"] for row in cohorts) == 91

assert all(
    row["activity_pct"] is None
    for row in cohorts
    if not row["observable"]
)

assert all(
    row["activity_pct"] is not None
    for row in cohorts
    if row["observable"]
)

print("SIX CUSTOMER SEGMENTS: PASS")
print("CUSTOMER POPULATION RECONCILIATION: PASS")
print("DELIVERED ORDER RECONCILIATION: PASS")
print("GROSS ITEM VALUE RECONCILIATION: PASS")
print("COHORT OBSERVATION MASKING: PASS")
print("CUSTOMER INTELLIGENCE DATA FOUNDATION: PASS")
