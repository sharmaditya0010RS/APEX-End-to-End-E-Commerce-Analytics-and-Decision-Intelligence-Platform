from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

import dash
from dash import dcc

from app import app
from customer_charts import (
    build_customer_figures,
    build_customer_additional_figures
)
from data_access import (
    customer_intelligence_data,
    customer_rfm_distributions
)

data = customer_intelligence_data()
segments = data["segments"]
cohorts = data["cohorts"]

assert len(segments) == 6
assert sum(r["customers"] for r in segments) == 93358
assert sum(r["orders"] for r in segments) == 96478
assert len(cohorts) == 299

first_three = build_customer_figures("customers", "all", 12)
additional = build_customer_additional_figures("all")

assert len(first_three) == 3
assert len(additional) == 7

repeat_counts = additional[0].data[0].values
assert sum(repeat_counts) == 93358
assert int(repeat_counts[1]) == 2801

assert len(additional[1].data[0].x) == 6
assert len(additional[2].data[0].x) == 6

distribution = customer_rfm_distributions("all")

for dimension in ["frequency", "recency", "monetary"]:
    assert sum(distribution[dimension].values()) == 93358

assert sum(additional[3].data[0].y) == 93358
assert sum(additional[4].data[0].y) == 93358
assert sum(additional[5].data[0].y) == 93358

assert len(additional[6].data[0].x) == 23
assert sum(additional[6].data[0].y) == 93358

filtered = build_customer_additional_figures("Repeat Champions")

assert sum(filtered[3].data[0].y) == 1310
assert sum(filtered[4].data[0].y) == 1310
assert sum(filtered[5].data[0].y) == 1310
assert sum(filtered[6].data[0].y) == 93358

page = next(
    entry for entry in dash.page_registry.values()
    if entry["path"] == "/customers"
)

def graph_ids(node):
    found = []
    if isinstance(node, dcc.Graph):
        found.append(node.id)

    children = getattr(node, "children", None)

    if isinstance(children, (list, tuple)):
        for child in children:
            found.extend(graph_ids(child))
    elif children is not None:
        found.extend(graph_ids(children))

    return found

ids = graph_ids(page["layout"]())

assert len(ids) == 10, ids
assert len(set(ids)) == 10

app._setup_server()

assert any(
    "customer-repeat-chart" in output
    and "customer-acquisition-chart" in output
    for output in app.callback_map
)

print("CUSTOMER BASELINE: PASS")
print("REPEAT CUSTOMER RECONCILIATION: PASS")
print("THREE RFM DISTRIBUTIONS: PASS")
print("CUSTOMER SEGMENT FILTER: PASS")
print("ACQUISITION COHORT RECONCILIATION: PASS")
print("TEN UNIQUE CUSTOMER CHART COMPONENTS: PASS")
print("SEVEN-OUTPUT CALLBACK REGISTRATION: PASS")
print("PHASE 8.6 CUSTOMER INTELLIGENCE: PASS")
