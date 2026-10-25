from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

from app import app
from data_access import executive_monthly_trends
from executive_charts import build_executive_figures

rows = executive_monthly_trends(
    "2017-01-01",
    "2018-08-31"
)

assert len(rows) == 20, len(rows)
assert rows[0]["month"] == "2017-01-01"
assert rows[-1]["month"] == "2018-08-01"

assert sum(row["eligible_orders"] for row in rows) == 96203
assert sum(row["late_orders"] for row in rows) == 6531

assert all(row["orders"] > 0 for row in rows)
assert all(row["gross_item_value"] >= 0 for row in rows)

figures = build_executive_figures(
    "2017-01-01",
    "2018-08-31"
)

assert len(figures) == 3

for index, figure in enumerate(figures, start=1):
    assert len(figure.data) == 1
    assert len(figure.data[0]["x"]) == len(rows)
    assert len(figure.data[0]["y"]) == len(rows)
    print(f"EXECUTIVE VISUAL {index}: PASS")

short_rows = executive_monthly_trends(
    "2018-07-01",
    "2018-08-31"
)

assert len(short_rows) == 2
assert sum(row["eligible_orders"] for row in short_rows) == 12507
assert sum(row["late_orders"] for row in short_rows) == 601

short_figures = build_executive_figures(
    "2018-07-01",
    "2018-08-31"
)

assert all(
    len(figure.data[0]["x"]) == 2
    for figure in short_figures
)

app._setup_server()

registered_outputs = [
    output
    for output in app.callback_map
    if "executive-order-momentum" in output
    and "executive-gross-value" in output
    and "executive-sla-trend" in output
]

assert len(registered_outputs) == 1, app.callback_map.keys()

print("POSTGRESQL TREND RECONCILIATION: PASS")
print("DATE-FILTERED CHART GENERATION: PASS")
print("DASH CALLBACK REGISTRATION: PASS")
print("PHASE 8.2 FIRST THREE VISUALS: PASS")
