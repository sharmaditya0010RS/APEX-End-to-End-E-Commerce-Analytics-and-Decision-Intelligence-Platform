import dash
from dash import Input, Output, dcc, html

from data_access import operations_states
from operations_charts import build_operations_figures, build_operations_additional_figures

dash.register_page(
    __name__,
    path="/operations",
    name="Operations & Logistics",
    order=2
)

CHARTS = [
    (
        "21",
        "Monthly Delivery SLA Rate",
        "Late-delivery percentage among eligible delivered orders",
        "operations-sla-chart"
    ),
    (
        "22",
        "Delivery Duration Distribution",
        "Actual purchase-to-delivery durations, grouped into bands",
        "operations-duration-chart"
    ),
    (
        "23",
        "Promised vs Actual Delivery",
        "Five-day duration bins; bubble size represents order count",
        "operations-comparison-chart"
    )
]


EXTRA_CHARTS = [
    ("24", "Geographic Delivery Risk", "Late rates across states with at least 100 eligible orders", "operations-geographic-risk"),
    ("25", "Monthly Delivery Outcomes", "Historical on-time and late order counts", "operations-outcome-mix"),
    ("26", "Freight Cost Distribution", "Recorded order-level freight-charge bands", "operations-freight-distribution"),
    ("27", "Freight Burden by State", "Freight relative to gross item value by customer state", "operations-freight-states"),
    ("28", "Top Sellers by Order Volume", "Seller-order pairs, not unique marketplace orders", "operations-seller-volume"),
    ("29", "Seller Delivery Risk", "Highest late rates among sellers with at least 30 eligible pairs", "operations-seller-risk"),
    ("30", "Delivery Reviews & SLA", "Rounded order-average review score by delivery outcome", "operations-review-sla")
]

def chart_card(number, title, subtitle, graph_id, wide=False):
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
                        id=graph_id,
                        responsive=True,
                        style={
                            "height": "410px" if wide else "330px",
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
        className=(
            "apex-graph-card operations-wide"
            if wide else "apex-graph-card"
        )
    )


def layout(**kwargs):
    states = operations_states()

    return html.Div(
        [
            html.Div("03 / OPERATIONS INTELLIGENCE", className="eyebrow"),
            html.H1("Operations & Logistics"),
            html.P(
                "Historical delivery reliability, fulfillment duration and promised-versus-actual outcomes.",
                className="page-description"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("PURCHASE DATE RANGE", className="filter-label"),
                            dcc.DatePickerRange(
                                id="operations-date-range",
                                min_date_allowed="2017-01-01",
                                max_date_allowed="2018-08-31",
                                start_date="2017-01-01",
                                end_date="2018-08-31",
                                display_format="DD MMM YYYY",
                                clearable=False
                            )
                        ],
                        className="operations-filter"
                    ),
                    html.Div(
                        [
                            html.Label("CUSTOMER STATE", className="filter-label"),
                            dcc.Dropdown(
                                id="operations-state",
                                options=[
                                    {"label": "All states", "value": "all"}
                                ] + [
                                    {"label": state, "value": state}
                                    for state in states
                                ],
                                value="all",
                                clearable=False
                            )
                        ],
                        className="operations-filter"
                    )
                ],
                className="operations-filter-bar"
            ),
            html.Div(
                [
                    chart_card(*CHARTS[0]),
                    chart_card(*CHARTS[1]),
                    chart_card(*CHARTS[2], wide=True),
                    chart_card(*EXTRA_CHARTS[0]),
                    chart_card(*EXTRA_CHARTS[1]),
                    chart_card(*EXTRA_CHARTS[2]),
                    chart_card(*EXTRA_CHARTS[3]),
                    chart_card(*EXTRA_CHARTS[4]),
                    chart_card(*EXTRA_CHARTS[5]),
                    chart_card(*EXTRA_CHARTS[6], wide=True)
                ],
                className="operations-chart-grid"
            ),
            html.P(
                "Source: historical Olist delivered orders. SLA lateness is defined by calendar date. Duration charts describe historical outcomes, not causal logistics effects.",
                className="chart-footnote"
            )
        ]
    )


@dash.callback(
    Output("operations-sla-chart", "figure"),
    Output("operations-duration-chart", "figure"),
    Output("operations-comparison-chart", "figure"),
    Input("operations-date-range", "start_date"),
    Input("operations-date-range", "end_date"),
    Input("operations-state", "value")
)
def update_operations_charts(start_date, end_date, state):
    return build_operations_figures(start_date, end_date, state)


@dash.callback(
    Output("operations-geographic-risk", "figure"),
    Output("operations-outcome-mix", "figure"),
    Output("operations-freight-distribution", "figure"),
    Output("operations-freight-states", "figure"),
    Output("operations-seller-volume", "figure"),
    Output("operations-seller-risk", "figure"),
    Output("operations-review-sla", "figure"),
    Input("operations-date-range", "start_date"),
    Input("operations-date-range", "end_date"),
    Input("operations-state", "value")
)
def update_operations_additional_charts(start_date, end_date, state):
    return build_operations_additional_figures(start_date, end_date, state)
