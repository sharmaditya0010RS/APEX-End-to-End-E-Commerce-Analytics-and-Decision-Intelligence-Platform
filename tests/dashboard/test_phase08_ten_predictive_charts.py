from pathlib import Path
import sys
import math

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

import dash
from dash import dcc

from app import app
from predictive_data import predictive_evidence
from predictive_charts import build_predictive_figures

data = predictive_evidence()
test = data["test"]
budgets = data["budgets"]
board = data["leaderboard"]

assert len(board) == 5
assert len(budgets) == 6
assert int(test["test_rows"]) == 12507
assert int(test["test_late_orders"]) == 601

figures = build_predictive_figures("expanded_logistic", 5)

assert len(figures) == 10

for i, figure in enumerate(figures, start=31):
    assert len(figure.data) >= 1
    assert len(figure.to_json()) > 300
    assert figure.layout.height == 330
    print(f"PREDICTIVE VISUAL {i}: PASS")

for index, metric in enumerate([
    "validation_average_precision",
    "validation_roc_auc",
    "validation_brier_score"
]):
    assert math.isclose(
        sum(float(v) for v in figures[index].data[0].x),
        float(board[metric].sum()),
        rel_tol=1e-9
    )

matrix = figures[4].data[0].z
assert sum(sum(int(v) for v in row) for row in matrix) == 12507

capture = figures[5]
assert len(capture.data) == 3
assert float(capture.data[2].x[0]) == 5

calibration = figures[7]
assert len(calibration.data[1].x) == len(data["calibration"])

monthly = figures[8]
assert len(monthly.data) == 2
assert len(monthly.data[0].x) == 2

filtered = build_predictive_figures("strict_logistic", 10)
assert len(filtered) == 10
assert float(filtered[5].data[2].x[0]) == 10

page = next(
    entry for entry in dash.page_registry.values()
    if entry["path"] == "/predictive"
)

def graph_ids(node):
    found = []
    if isinstance(node, dcc.Graph):
        found.append(node.id)
    children = getattr(node, "children", None)
    if isinstance(children, (tuple, list)):
        for child in children:
            found.extend(graph_ids(child))
    elif children is not None:
        found.extend(graph_ids(children))
    return found

ids = graph_ids(page["layout"]())
assert len(ids) == 10
assert len(set(ids)) == 10

app._setup_server()

matches = [
    key for key in app.callback_map
    if "predictive-visual-31" in key
    and "predictive-visual-40" in key
]
assert len(matches) == 1

print("FIVE MODEL EXPERIMENTS: PASS")
print("HELD-OUT CONFUSION MATRIX: PASS")
print("CALIBRATION AND MONTHLY COUNTS: PASS")
print("MODEL AND CAPACITY FILTERS: PASS")
print("TEN UNIQUE PREDICTIVE GRAPH COMPONENTS: PASS")
print("TEN-OUTPUT DASH CALLBACK: PASS")
print("PHASE 8.10 PREDICTIVE INTELLIGENCE: PASS")
