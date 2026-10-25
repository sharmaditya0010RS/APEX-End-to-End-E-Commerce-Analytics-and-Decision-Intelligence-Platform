from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

import dash
from dash import dcc
from app import app
from data_access import (
    operations_delivery_data,
    operations_additional_data
)
from operations_charts import (
    build_operations_figures,
    build_operations_additional_figures
)

start = "2017-01-01"
end = "2018-08-31"

original = operations_delivery_data(start, end)
additional_data = operations_additional_data(start, end)

eligible = sum(row["eligible"] for row in original["monthly"])
late = sum(row["late"] for row in original["monthly"])

assert eligible == 96203
assert late == 6531

assert sum(
    row["eligible"] for row in additional_data["geography"]
) == eligible

assert sum(
    row["late"] for row in additional_data["geography"]
) == late

assert sum(
    row["on_time"] + row["late"]
    for row in additional_data["monthly"]
) == eligible

assert sum(
    row["orders"] for row in additional_data["freight"]
) == eligible

assert all(
    0 <= row["late"] <= row["eligible"]
    for row in additional_data["sellers"]
)

assert all(
    1 <= row["score"] <= 5
    for row in additional_data["reviews"]
)

first = build_operations_figures(start, end)
second = build_operations_additional_figures(start, end)
figures = (*first, *second)

assert len(first) == 3
assert len(second) == 7
assert len(figures) == 10

for number, figure in enumerate(figures, start=21):
    assert len(figure.data) >= 1
    assert len(figure.to_json()) > 300
    print(f"OPERATIONS VISUAL {number}: PASS")

assert sum(second[1].data[0].y) + sum(
    second[1].data[1].y
) == eligible

assert sum(second[2].data[0].y) == eligible

assert all(
    len(trace.y) <= 12
    for trace in [second[0].data[0], second[3].data[0],
                  second[4].data[0], second[5].data[0]]
)

filtered = operations_additional_data(
    "2018-07-01", "2018-08-31", "SP"
)

filtered_eligible = sum(
    row["eligible"] for row in filtered["geography"]
)

assert 0 < filtered_eligible < 12507

filtered_figures = build_operations_additional_figures(
    "2018-07-01", "2018-08-31", "SP"
)

assert len(filtered_figures) == 7

page = next(
    entry for entry in dash.page_registry.values()
    if entry["path"] == "/operations"
)

def graph_ids(node):
    result = []
    if isinstance(node, dcc.Graph):
        result.append(node.id)
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            result.extend(graph_ids(child))
    elif children is not None:
        result.extend(graph_ids(children))
    return result

ids = graph_ids(page["layout"]())

assert len(ids) == 10, ids
assert len(set(ids)) == 10

app._setup_server()

assert any(
    "operations-geographic-risk" in key
    and "operations-review-sla" in key
    for key in app.callback_map
)

print("GEOGRAPHIC SLA COUNTS: PASS")
print("MONTHLY OUTCOME COUNTS: PASS")
print("FREIGHT DISTRIBUTION COUNTS: PASS")
print("SELLER SAMPLE VALIDITY: PASS")
print("STATE AND DATE FILTER: PASS")
print("TEN UNIQUE GRAPH COMPONENTS: PASS")
print("OPERATIONS CALLBACK REGISTRATION: PASS")
print("PHASE 8.9 OPERATIONS TEN-CHART VALIDATION: PASS")
