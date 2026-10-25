from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

from app import app
from customer_charts import build_customer_figures
from data_access import customer_intelligence_data
import dash
from dash import dcc

data = customer_intelligence_data()
segments = data["segments"]
cohorts = data["cohorts"]

assert len(segments) == 6
assert sum(r["customers"] for r in segments) == 93358
assert sum(r["orders"] for r in segments) == 96478
assert len(cohorts) == 299

figures = build_customer_figures("customers", "all", 12)

assert len(figures) == 3
assert sum(figures[0].data[0].x) == 93358
assert abs(sum(figures[1].data[0].values) - 13221498.11) < 0.02

matrix = figures[2].data[0].z
assert len(matrix) == 23
assert all(len(row) == 13 for row in matrix)

plotted = [value for row in matrix for value in row]
assert sum(value is None for value in plotted) == 91
assert sum(value == 0 for value in plotted if value is not None) == 33

short_figures = build_customer_figures(
    "orders", "Repeat Champions", 3
)

assert sum(short_figures[0].data[0].x) == 96478
assert len(short_figures[2].data[0].x) == 4
assert len(short_figures[2].data[0].z) == 23

page = next(
    item for item in dash.page_registry.values()
    if item["path"] == "/customers"
)

layout = page["layout"]()

def collect_graphs(node):
    result = []
    if isinstance(node, dcc.Graph):
        result.append(node)
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            result.extend(collect_graphs(child))
    elif children is not None:
        result.extend(collect_graphs(children))
    return result

graphs = collect_graphs(layout)

assert len(graphs) == 10
assert {
    "customer-segments-chart",
    "customer-value-chart",
    "customer-cohort-chart"
}.issubset({graph.id for graph in graphs})
assert len({graph.id for graph in graphs}) == 10

app._setup_server()
assert any(
    "customer-segments-chart" in key
    and "customer-cohort-chart" in key
    for key in app.callback_map
)

print("CUSTOMER SEGMENT COUNT RECONCILIATION: PASS")
print("GROSS VALUE RECONCILIATION: PASS")
print("COHORT OBSERVABILITY MASK: PASS")
print("SEGMENT AND HORIZON FILTERS: PASS")
print("THREE CUSTOMER GRAPH COMPONENTS: PASS")
print("DASH CUSTOMER CALLBACK REGISTRATION: PASS")
print("PHASE 8.5 CUSTOMER VISUALS 11-13: PASS")
