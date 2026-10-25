import dash
from dash import Input, Output, dcc, html

from predictive_data import predictive_evidence
from predictive_charts import build_predictive_figures

dash.register_page(
    __name__,
    path="/predictive",
    name="Predictive Intelligence",
    order=3
)

CHARTS = [
    ("31", "Average Precision Leaderboard", "Validation rankings · Higher is better"),
    ("32", "ROC-AUC Leaderboard", "Validation discrimination · Higher is better"),
    ("33", "Brier Score Leaderboard", "Validation probability error · Lower is better"),
    ("34", "Validation vs Test Performance", "Selected model only · Chronological evaluation"),
    ("35", "Held-Out Confusion Matrix", "Locked F2 threshold · July–August 2018"),
    ("36", "Review Capacity vs Capture", "Historical late orders identified · Not prevented"),
    ("37", "Precision at Review Capacity", "Selected capacity highlighted against test prevalence"),
    ("38", "Probability Calibration", "Held-out score bins versus observed event rates"),
    ("39", "Monthly Prediction Drift", "Predicted risk versus actual late-delivery rate"),
    ("40", "Monthly Calibration Gap", "Positive gap means predicted risk exceeded observed rate")
]

IDS = [f"predictive-visual-{i}" for i in range(31, 41)]


def chart_card(index, wide=False):
    number, title, subtitle = CHARTS[index]
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
                        style={"height": "330px", "width": "100%"},
                        responsive=True,
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
        className=(
            "apex-graph-card predictive-wide"
            if wide else "apex-graph-card"
        )
    )


def layout(**kwargs):
    evidence = predictive_evidence()
    test = evidence["test"]
    selection = evidence["selection"]
    board = evidence["leaderboard"]

    def kpi(label, value, detail):
        return html.Div(
            [
                html.Div(label, className="metric-label"),
                html.Div(value, className="metric-value"),
                html.Div(detail, className="metric-detail")
            ],
            className="metric-card"
        )

    return html.Div(
        [
            html.Div("04 / MODEL INTELLIGENCE", className="eyebrow"),
            html.H1("Predictive Intelligence"),
            html.P(
                "Chronological model validation, held-out risk ranking and calibration diagnostics. Historical research only.",
                className="page-description"
            ),
            html.Div(
                [
                    kpi(
                        "HELD-OUT ORDERS",
                        f"{int(test['test_rows']):,}",
                        "July–August 2018"
                    ),
                    kpi(
                        "TEST AVERAGE PRECISION",
                        f"{test['test_average_precision']:.4f}",
                        "Test prevalence baseline: 0.0481"
                    ),
                    kpi(
                        "TEST ROC-AUC",
                        f"{test['test_roc_auc']:.4f}",
                        "Selected expanded logistic model"
                    ),
                    kpi(
                        "TEST RECALL",
                        f"{test['test_recall']:.1%}",
                        "At validation-locked classification threshold"
                    )
                ],
                className="metric-grid"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("HIGHLIGHT VALIDATION MODEL", className="filter-label"),
                            dcc.Dropdown(
                                id="predictive-model-filter",
                                options=[
                                    {"label": name.replace("_", " ").title(), "value": name}
                                    for name in board["model"]
                                ],
                                value=selection["selected_model"],
                                clearable=False
                            )
                        ],
                        className="predictive-filter"
                    ),
                    html.Div(
                        [
                            html.Label("ORDER REVIEW CAPACITY", className="filter-label"),
                            dcc.Dropdown(
                                id="predictive-capacity-filter",
                                options=[
                                    {"label": f"Top {v}% of orders", "value": v}
                                    for v in [1, 5, 10, 20, 50, 100]
                                ],
                                value=5,
                                clearable=False
                            )
                        ],
                        className="predictive-filter"
                    )
                ],
                className="predictive-filter-bar"
            ),
            html.Div(
                [chart_card(i, wide=i in (5, 7)) for i in range(10)],
                className="predictive-chart-grid"
            ),
            html.P(
                "Model highlighting applies only to validation leaderboards. All held-out test charts refer to the originally selected expanded logistic model. Raw probabilities are not deployment-approved.",
                className="chart-footnote"
            )
        ]
    )


@dash.callback(
    *[Output(graph_id, "figure") for graph_id in IDS],
    Input("predictive-model-filter", "value"),
    Input("predictive-capacity-filter", "value")
)
def update_predictive_charts(model, capacity):
    return build_predictive_figures(model, capacity)
