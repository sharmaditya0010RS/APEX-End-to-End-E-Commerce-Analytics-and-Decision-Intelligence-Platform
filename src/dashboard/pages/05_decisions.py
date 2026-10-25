import dash
from dash import Input, Output, dcc, html

from decision_data import (
    decision_evidence,
    selected_scenario,
    CAPACITIES,
    EFFECTIVENESS,
    COSTS,
    VALUES
)
from decision_charts import build_decision_figures

dash.register_page(
    __name__,
    path="/decisions",
    name="Decision Scenario Lab",
    order=4
)

DETAILS = [
    ("41", "Scenario Net Value Distribution", "All 162 hypothetical scenarios; selected scenario marked"),
    ("42", "Benefit, Cost and Net", "Selected scenario financial decomposition"),
    ("43", "Review Capacity Sensitivity", "Model-ranked versus expected random review"),
    ("44", "Review Cost Sensitivity", "One-dimensional assumed cost comparison"),
    ("45", "Effectiveness Sensitivity", "Unobserved intervention success-rate assumptions"),
    ("46", "Preventable Value Sensitivity", "Hypothetical value per successfully prevented late order"),
    ("47", "Break-Even Value Frontier", "Required preventable value compared with the selected assumption"),
    ("48", "Reference-Case Outcomes", "Six documented reference cases; all financially nonviable"),
    ("49", "Incremental Model Advantage", "Hypothetical model net minus expected random net"),
    ("50", "Decision Feasibility Heatmap", "Value versus review cost at selected capacity and effectiveness")
]

IDS = [f"decision-visual-{n}" for n in range(41, 51)]


def chart_card(index, large=False):
    number, title, subtitle = DETAILS[index]
    return html.Section(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Span(number, className="chart-index"),
                            html.H3(title, className="chart-heading")
                        ],
                        className="chart-heading-row"
                    ),
                    html.P(subtitle, className="chart-subheading")
                ],
                className="chart-card-header"
            ),
            html.Div(
                dcc.Loading(
                    dcc.Graph(
                        id=IDS[index],
                        responsive=True,
                        style={
                            "height": "410px" if large else "330px",
                            "width": "100%"
                        },
                        config={
                            "displaylogo": False,
                            "scrollZoom": False
                        }
                    ),
                    type="circle"
                ),
                className="chart-body"
            )
        ],
        className="apex-graph-card decision-large" if large
        else "apex-graph-card"
    )


def layout(**kwargs):
    evidence = decision_evidence()
    scenarios = evidence["scenarios"]
    positive = int((scenarios["model_scenario_net_brl"] > 0).sum())

    def metric(label, value, detail, output_id=None):
        return html.Div(
            [
                html.Div(label, className="metric-label"),
                html.Div(
                    value,
                    **({"id": output_id} if output_id is not None else {}),
                    className="metric-value"
                ),
                html.Div(detail, className="metric-detail")
            ],
            className="metric-card"
        )

    def choice(label, element):
        return html.Div(
            [html.Label(label, className="filter-label"), element],
            className="decision-filter"
        )

    return html.Div(
        [
            html.Div("05 / DECISION INTELLIGENCE", className="eyebrow"),
            html.H1("Decision Scenario Lab"),
            html.P(
                "Financial stress tests of historical risk-ranking evidence. All intervention effects and savings are hypothetical.",
                className="page-description"
            ),
            html.Div(
                [
                    metric("SCENARIO GRID", "162", "Documented Phase 7 combinations"),
                    metric(
                        "POSITIVE WHAT-IF CASES",
                        str(positive),
                        "Hypothetical only; not realized savings"
                    ),
                    metric(
                        "REFERENCE DECISION",
                        "NO-GO",
                        "All six reference cases are negative"
                    ),
                    metric(
                        "SELECTED SCENARIO NET",
                        "Loading",
                        "Assumptions-based BRL estimate",
                        "decision-selected-net"
                    )
                ],
                className="metric-grid"
            ),
            html.Div(
                [
                    choice(
                        "REVIEW CAPACITY",
                        dcc.Dropdown(
                            id="decision-capacity",
                            options=[
                                {"label": f"Top {v}% of test orders", "value": v}
                                for v in CAPACITIES
                            ],
                            value=5, clearable=False
                        )
                    ),
                    choice(
                        "ASSUMED EFFECTIVENESS",
                        dcc.Dropdown(
                            id="decision-effectiveness",
                            options=[
                                {"label": f"{v:.0%} prevented", "value": v}
                                for v in EFFECTIVENESS
                            ],
                            value=0.25, clearable=False
                        )
                    ),
                    choice(
                        "REVIEW COST",
                        dcc.Dropdown(
                            id="decision-cost",
                            options=[
                                {"label": f"R${v} per reviewed order", "value": v}
                                for v in COSTS
                            ],
                            value=5, clearable=False
                        )
                    ),
                    choice(
                        "VALUE PER PREVENTION",
                        dcc.Dropdown(
                            id="decision-value",
                            options=[
                                {"label": f"R${v} per prevented late", "value": v}
                                for v in VALUES
                            ],
                            value=50, clearable=False
                        )
                    )
                ],
                className="decision-filter-bar"
            ),
            html.Div(
                [chart_card(i, large=(i == 9)) for i in range(10)],
                className="decision-chart-grid"
            ),
            html.P(
                "Interpretation: model outcomes describe retrospective ranking on 12,507 held-out orders. Random comparison is an expected-value baseline. No intervention effectiveness or realized financial benefit was measured. Positive what-if scenarios do not override the reference-case conditional no-go.",
                className="chart-footnote"
            )
        ]
    )


@dash.callback(
    *[Output(chart_id, "figure") for chart_id in IDS],
    Output("decision-selected-net", "children"),
    Input("decision-capacity", "value"),
    Input("decision-effectiveness", "value"),
    Input("decision-cost", "value"),
    Input("decision-value", "value")
)
def update_decisions(capacity, effectiveness, cost, value):
    figures = build_decision_figures(capacity, effectiveness, cost, value)
    record = selected_scenario(
        decision_evidence(), capacity, effectiveness, cost, value
    )
    formatted = f"R${float(record['model_scenario_net_brl']):+,.2f}"
    return (*figures, formatted)
