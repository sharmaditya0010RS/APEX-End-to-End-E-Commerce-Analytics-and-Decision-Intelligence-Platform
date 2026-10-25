from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

from dash import dcc
import dash

from decision_data import decision_evidence, selected_scenario
from decision_charts import build_decision_figures
from app import app

data = decision_evidence()
scenarios = data["scenarios"]
reference = data["break_even"]

assert len(scenarios) == 162
assert len(reference) == 6
assert int(data["manifest"]["test_orders"]) == 12507
assert int(data["manifest"]["observed_test_late_orders"]) == 601

selected = selected_scenario(data, 5, 0.25, 5, 50)
assert np.isclose(selected["model_scenario_net_brl"], -2217.5)

figures = build_decision_figures(5, 0.25, 5, 50)
assert len(figures) == 10

for number, figure in enumerate(figures, 41):
    assert len(figure.data) > 0
    assert len(figure.to_json()) > 300
    assert figure.layout.title.text is None
    print(f"DECISION VISUAL {number}: PASS")

capacity = figures[2]
assert len(capacity.data[0].x) == 6
assert len(capacity.data[1].x) == 6

assert len(figures[3].data[0].x) == 3
assert len(figures[4].data[0].x) == 3
assert len(figures[5].data[0].x) == 3

assert len(figures[6].data[0].x) == 6
assert len(figures[7].data[0].x) == 6

heatmap = figures[9].data[0]
assert len(heatmap.x) == 3
assert len(heatmap.y) == 3
assert np.isclose(float(heatmap.z[1][1]), -2217.5)

alternative = build_decision_figures(1, 0.1, 2, 100)
assert len(alternative) == 10
assert np.isclose(float(alternative[9].data[0].z[0][2]), 28)

page = next(
    row for row in dash.page_registry.values()
    if row["path"] == "/decisions"
)

def collect_graph_ids(node):
    result = []
    if isinstance(node, dcc.Graph):
        result.append(node.id)
    children = getattr(node, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            result.extend(collect_graph_ids(child))
    elif children is not None:
        result.extend(collect_graph_ids(children))
    return result

ids = collect_graph_ids(page["layout"]())
assert len(ids) == 10, ids
assert len(set(ids)) == 10

app._setup_server()

matches = [
    key for key in app.callback_map
    if "decision-visual-41" in key
    and "decision-visual-50" in key
    and "decision-selected-net" in key
]
assert len(matches) == 1, matches

payload = {
    "output": matches[0],
    "outputs": [
        {"id": chart_id, "property": "figure"}
        for chart_id in ids
    ] + [
        {"id": "decision-selected-net", "property": "children"}
    ],
    "inputs": [
        {"id": "decision-capacity", "property": "value", "value": 5},
        {"id": "decision-effectiveness", "property": "value", "value": 0.25},
        {"id": "decision-cost", "property": "value", "value": 5},
        {"id": "decision-value", "property": "value", "value": 50}
    ],
    "state": [],
    "changedPropIds": ["decision-capacity.value"]
}

response = app.server.test_client().post(
    "/_dash-update-component", json=payload
)

print("DECISION CALLBACK HTTP STATUS:", response.status_code)

if response.status_code != 200:
    print(response.get_data(as_text=True)[:4000])
    raise RuntimeError("Decision callback HTTP failure")

body = response.get_json()["response"]

for chart_id in ids:
    figure = body[chart_id]["figure"]
    assert len(figure["data"]) > 0

assert body["decision-selected-net"]["children"] == "R$-2,217.50"

print("162 SCENARIOS RECONCILED: PASS")
print("SIX NO-GO REFERENCE CASES: PASS")
print("SELECTED SCENARIO ARITHMETIC: PASS")
print("CAPACITY AND THREE-WAY SENSITIVITY: PASS")
print("BREAK-EVEN FRONTIER: PASS")
print("TEN DISTINCT GRAPH COMPONENTS: PASS")
print("TEN-OUTPUT HTTP CALLBACK: PASS")
print("PHASE 8.11 DECISION LAB VALIDATION: PASS")
