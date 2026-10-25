from pathlib import Path
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "dashboard"))

import dash
from dash import dcc
from app import app
from data_access import executive_breakdowns, executive_monthly_trends
from executive_charts import (
    build_executive_figures,
    build_executive_additional_figures
)

def inspect_period(start, end, expected_months):
    trends = executive_monthly_trends(start, end)
    breakdown = executive_breakdowns(start, end)

    assert len(trends) == expected_months

    total_orders = sum(row["orders"] for row in trends)
    status_orders = sum(row["orders"] for row in breakdown["status"])
    state_orders = sum(row["orders"] for row in breakdown["states"])
    basket_orders = sum(row["orders"] for row in breakdown["basket"])
    monthly_orders = sum(row["orders"] for row in breakdown["monthly"])

    assert total_orders == status_orders
    assert total_orders == state_orders
    assert total_orders == basket_orders
    assert total_orders == monthly_orders

    trend_value = sum(row["gross_item_value"] for row in trends)
    breakdown_value = sum(row["item_value"] for row in breakdown["monthly"])

    assert math.isclose(trend_value, breakdown_value, abs_tol=0.02)

    state_value = sum(row["item_value"] for row in breakdown["states"])
    assert math.isclose(trend_value, state_value, abs_tol=0.02)

    first = build_executive_figures(start, end)
    additional = build_executive_additional_figures(start, end)
    all_figures = (*first, *additional)

    assert len(first) == 3
    assert len(additional) == 7
    assert len(all_figures) == 10

    for figure in all_figures:
        assert len(figure.data) >= 1
        assert figure.layout.title.text is None
        assert figure.layout.height == 330
        assert len(figure.to_json()) > 300

    expected_month_values = [
        row["orders"] for row in trends
    ]
    assert list(first[0].data[0].y) == expected_month_values

    expected_status_values = sorted(
        [row["orders"] for row in breakdown["status"]]
    )
    actual_status_values = sorted(
        [int(value) for value in additional[0].data[0].values]
    )
    assert actual_status_values == expected_status_values

    stacked = additional[6]
    assert len(stacked.data) == 2
    assert sum(stacked.data[0].y) + sum(stacked.data[1].y) == sum(
        row["eligible_orders"] for row in trends
    )
    assert sum(stacked.data[1].y) == sum(
        row["late_orders"] for row in trends
    )

    print(
        f"PERIOD {start} TO {end}: PASS | "
        f"{total_orders:,} orders | 10 figures"
    )
    return trends

full = inspect_period("2017-01-01", "2018-08-31", 20)
recent = inspect_period("2018-07-01", "2018-08-31", 2)

assert sum(row["eligible_orders"] for row in full) == 96203
assert sum(row["late_orders"] for row in full) == 6531

assert sum(row["eligible_orders"] for row in recent) == 12507
assert sum(row["late_orders"] for row in recent) == 601

executive_page = next(
    page for page in dash.page_registry.values()
    if page["path"] == "/"
)

page_layout = executive_page["layout"]()

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

graphs = collect_graphs(page_layout)
graph_ids = [graph.id for graph in graphs]

assert len(graphs) == 10, graph_ids
assert len(set(graph_ids)) == 10

app._setup_server()

registered_outputs = [
    output for output in app.callback_map
    if "executive-order-momentum" in output
    and "executive-delivery-outcomes" in output
]

assert len(registered_outputs) == 1, list(app.callback_map)

print("EXACTLY TEN EXECUTIVE GRAPH COMPONENTS: PASS")
print("TEN-OUTPUT DATE FILTER CALLBACK: PASS")
print("ORDER, GEOGRAPHY AND BASKET RECONCILIATION: PASS")
print("SLA OUTCOME RECONCILIATION: PASS")
print("PHASE 8.3 EXECUTIVE CHART TESTS: PASS")
