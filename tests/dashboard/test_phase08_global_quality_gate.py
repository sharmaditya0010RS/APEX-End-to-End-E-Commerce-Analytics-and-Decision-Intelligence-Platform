import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

import dash
from dash import dcc

from app import app

EXPECTED = {
    "/": 10,
    "/customers": 10,
    "/operations": 10,
    "/predictive": 10,
    "/decisions": 10,
}

def collect_graph_ids(node):
    ids = []

    if isinstance(node, dcc.Graph):
        ids.append(node.id)

    children = getattr(node, "children", None)

    if isinstance(children, (tuple, list)):
        for child in children:
            ids.extend(collect_graph_ids(child))
    elif children is not None:
        ids.extend(collect_graph_ids(children))

    return ids

registered = {
    entry["path"]: entry
    for entry in dash.page_registry.values()
}

assert set(registered) == set(EXPECTED), sorted(registered)

all_ids = []

for route, expected_count in EXPECTED.items():
    entry = registered[route]
    layout = entry["layout"]

    if callable(layout):
        layout = layout()

    ids = collect_graph_ids(layout)

    assert len(ids) == expected_count, (
        f"{route}: expected {expected_count}, found {len(ids)}"
    )

    assert len(ids) == len(set(ids)), (
        f"{route}: duplicate graph IDs"
    )

    print(f"{route}: {len(ids)}/10 UNIQUE GRAPHS — PASS")
    all_ids.extend(ids)

duplicates = [
    graph_id
    for graph_id, count in Counter(all_ids).items()
    if count > 1
]

assert not duplicates, duplicates
assert len(all_ids) == 50

app._setup_server()

callback_outputs = []

for callback in app.callback_map.values():
    outputs = callback["output"]
    if not isinstance(outputs, (list, tuple)):
        outputs = [outputs]

    for output in outputs:
        if output.component_property == "figure":
            callback_outputs.append(output.component_id)

missing = sorted(set(all_ids) - set(callback_outputs))
duplicate_outputs = [
    chart_id
    for chart_id, count in Counter(callback_outputs).items()
    if count > 1
]

assert not missing, f"Graphs without figure callbacks: {missing}"
assert not duplicate_outputs, duplicate_outputs
assert set(callback_outputs) == set(all_ids)

client = app.server.test_client()

for route in EXPECTED:
    response = client.get(route)
    assert response.status_code == 200, (
        route, response.status_code
    )

print("FIVE REGISTERED PAGES: PASS")
print("EXACTLY FIFTY UNIQUE GRAPH IDS: PASS")
print("ALL FIFTY FIGURE CALLBACK OUTPUTS: PASS")
print("NO DUPLICATE OUTPUT TARGETS: PASS")
print("FIVE HTTP ROUTES: PASS")
print("PHASE 8 GLOBAL GRAPH CENSUS: PASS")
