from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

import dash
from dash import dcc

from app import app
from data_access import operations_delivery_data, operations_states
from operations_charts import build_operations_figures

states = operations_states()
assert len(states) == 27
assert "SP" in states

full = operations_delivery_data(
    "2017-01-01",
    "2018-08-31"
)

recent = operations_delivery_data(
    "2018-07-01",
    "2018-08-31"
)

assert len(full["monthly"]) == 20
assert sum(row["eligible"] for row in full["monthly"]) == 96203
assert sum(row["late"] for row in full["monthly"]) == 6531

assert len(recent["monthly"]) == 2
assert sum(row["eligible"] for row in recent["monthly"]) == 12507
assert sum(row["late"] for row in recent["monthly"]) == 601

assert full["quality"]["eligible"] == 96203

duration_count = sum(
    row["orders"] for row in full["duration"]
)

assert (
    duration_count + full["quality"]["missing_actual"]
    == full["quality"]["eligible"]
)

comparison_count = sum(
    row["orders"] for row in full["comparison"]
)

assert (
    comparison_count
    + full["quality"]["missing_actual"]
    + full["quality"]["negative_actual"]
    == full["quality"]["eligible"]
)

figures = build_operations_figures(
    "2017-01-01",
    "2018-08-31"
)

assert len(figures) == 3
assert len(figures[0].data[0].x) == 20
assert sum(figures[1].data[0].y) == duration_count
assert sum(row["orders"] for row in full["comparison"]) == comparison_count

filtered = operations_delivery_data(
    "2018-07-01",
    "2018-08-31",
    "SP"
)

assert 0 < filtered["quality"]["eligible"] < 12507

filtered_figures = build_operations_figures(
    "2018-07-01",
    "2018-08-31",
    "SP"
)

assert len(filtered_figures) == 3
assert len(filtered_figures[0].data[0].x) == 2

page = next(
    entry for entry in dash.page_registry.values()
    if entry["path"] == "/operations"
)

def collect_graphs(node):
    found = []
    if isinstance(node, dcc.Graph):
        found.append(node.id)

    children = getattr(node, "children", None)

    if isinstance(children, (list, tuple)):
        for child in children:
            found.extend(collect_graphs(child))
    elif children is not None:
        found.extend(collect_graphs(children))

    return found

graph_ids = collect_graphs(page["layout"]())

assert len(graph_ids) == 10
assert {
    "operations-sla-chart",
    "operations-duration-chart",
    "operations-comparison-chart"
}.issubset(set(graph_ids))
assert len(set(graph_ids)) == 10

app._setup_server()

assert any(
    "operations-sla-chart" in output
    and "operations-duration-chart" in output
    and "operations-comparison-chart" in output
    for output in app.callback_map
)

print("27 CUSTOMER STATES: PASS")
print("MONTHLY SLA RECONCILIATION: PASS")
print("DELIVERY DURATION RECONCILIATION: PASS")
print("PROMISED/ACTUAL COMPARISON RECONCILIATION: PASS")
print("DATE AND STATE FILTERS: PASS")
print("THREE OPERATIONS GRAPHS: PASS")
print("THREE-OUTPUT CALLBACK REGISTRATION: PASS")
print("PHASE 8.8 OPERATIONS VISUALS 21-23: PASS")
print("QUALITY COUNTS:", full["quality"])
