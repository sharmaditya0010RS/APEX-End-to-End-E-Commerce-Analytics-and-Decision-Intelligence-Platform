import dash
from dash import Input, Output, dcc, html

from customer_charts import build_customer_figures, build_customer_additional_figures
from data_access import customer_intelligence_data

dash.register_page(
    __name__,
    path="/customers",
    name="Customer Intelligence",
    order=1
)

DETAILS = [
    ("11", "Customer Segment Distribution", "Delivered customers or orders across six mutually exclusive segments", "customer-segments-chart"),
    ("12", "Gross Item Value by Segment", "Relative contribution to observed delivered gross item value", "customer-value-chart"),
    ("13", "Cohort Repeat-Purchase Activity", "Monthly delivered-purchase activity; unobservable months are blank", "customer-cohort-chart")
]

EXTRA_DETAILS = [
    ("14", "One-Time vs Repeat Customers", "Whole-population observed purchase frequency", "customer-repeat-chart"),
    ("15", "Average Value by Segment", "Mean delivered gross item value per customer", "customer-average-value-chart"),
    ("16", "Average Recency by Segment", "Mean days since last delivered purchase", "customer-recency-segment-chart"),
    ("17", "Purchase Frequency Distribution", "Delivered-order frequency for selected segment scope", "customer-frequency-chart"),
    ("18", "Customer Recency Bands", "Recency distribution for selected segment scope", "customer-recency-bands-chart"),
    ("19", "Customer Monetary Bands", "Observed customer spending bands for selected segment scope", "customer-monetary-bands-chart"),
    ("20", "Acquisition Cohort Sizes", "First observed delivered-purchase cohorts by month", "customer-acquisition-chart")
]

def chart_card(number, title, subtitle, graph_id, large=False):
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
                        style={
                            "width": "100%",
                            "height": "550px" if large else "330px"
                        },
                        responsive=True,
                        config={"displaylogo": False, "scrollZoom": False}
                    ),
                    type="circle"
                ),
                className="chart-body"
            )
        ],
        className="apex-graph-card customer-cohort-card"
        if large else "apex-graph-card"
    )

def layout(**kwargs):
    data = customer_intelligence_data()
    segments = data["segments"]
    customers = sum(r["customers"] for r in segments)
    orders = sum(r["orders"] for r in segments)

    return html.Div(
        [
            html.Div("02 / CUSTOMER INTELLIGENCE", className="eyebrow"),
            html.H1("Customer Intelligence"),
            html.P(
                "Delivered-order customer segmentation and historically observed repeat purchasing.",
                className="page-description"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div("DELIVERED CUSTOMERS", className="metric-label"),
                            html.Div(f"{customers:,}", className="metric-value"),
                            html.Div("Observed delivered-order population", className="metric-detail")
                        ],
                        className="metric-card"
                    ),
                    html.Div(
                        [
                            html.Div("DELIVERED ORDERS", className="metric-label"),
                            html.Div(f"{orders:,}", className="metric-value"),
                            html.Div("Historical delivered purchases", className="metric-detail")
                        ],
                        className="metric-card"
                    ),
                    html.Div(
                        [
                            html.Div("OBSERVED REPEAT RATE", className="metric-label"),
                            html.Div("3.00%", className="metric-value"),
                            html.Div("2,801 repeat buyers, not a lifetime churn measure", className="metric-detail")
                        ],
                        className="metric-card"
                    ),
                    html.Div(
                        [
                            html.Div("CUSTOMER SEGMENTS", className="metric-label"),
                            html.Div("6", className="metric-value"),
                            html.Div("Mutually exclusive descriptive groups", className="metric-detail")
                        ],
                        className="metric-card"
                    )
                ],
                className="metric-grid"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("SEGMENT METRIC", className="filter-label"),
                            dcc.Dropdown(
                                id="customer-metric",
                                options=[
                                    {"label": "Customers", "value": "customers"},
                                    {"label": "Delivered orders", "value": "orders"}
                                ],
                                value="customers",
                                clearable=False
                            )
                        ],
                        className="customer-filter"
                    ),
                    html.Div(
                        [
                            html.Label("HIGHLIGHT SEGMENT", className="filter-label"),
                            dcc.Dropdown(
                                id="customer-highlight",
                                options=[{"label": "All segments", "value": "all"}]
                                + [
                                    {"label": r["segment"], "value": r["segment"]}
                                    for r in segments
                                ],
                                value="all",
                                clearable=False
                            )
                        ],
                        className="customer-filter"
                    ),
                    html.Div(
                        [
                            html.Label("COHORT HORIZON", className="filter-label"),
                            dcc.Dropdown(
                                id="customer-horizon",
                                options=[
                                    {"label": "3 months", "value": 3},
                                    {"label": "6 months", "value": 6},
                                    {"label": "12 months", "value": 12}
                                ],
                                value=12,
                                clearable=False
                            )
                        ],
                        className="customer-filter"
                    )
                ],
                className="customer-filter-bar"
            ),
            html.Div(
                [
                    chart_card(*DETAILS[0]),
                    chart_card(*DETAILS[1]),
                    chart_card(*DETAILS[2], large=True),
                    chart_card(*EXTRA_DETAILS[0]),
                    chart_card(*EXTRA_DETAILS[1]),
                    chart_card(*EXTRA_DETAILS[2]),
                    chart_card(*EXTRA_DETAILS[3]),
                    chart_card(*EXTRA_DETAILS[4]),
                    chart_card(*EXTRA_DETAILS[5]),
                    chart_card(*EXTRA_DETAILS[6])
                ],
                className="customer-chart-grid"
            ),
            html.P(
                "Segment highlighting changes charts 15–19; charts 14 and 20 remain whole-population views. Cohort cells show observed monthly delivered-purchase activity, not subscription retention. Blank cells are censored, not zero.",
                className="chart-footnote"
            )
        ]
    )

@dash.callback(
    Output("customer-segments-chart", "figure"),
    Output("customer-value-chart", "figure"),
    Output("customer-cohort-chart", "figure"),
    Input("customer-metric", "value"),
    Input("customer-highlight", "value"),
    Input("customer-horizon", "value")
)
def update_customer_charts(metric, selected_segment, horizon):
    return build_customer_figures(metric, selected_segment, horizon)


@dash.callback(
    Output("customer-repeat-chart", "figure"),
    Output("customer-average-value-chart", "figure"),
    Output("customer-recency-segment-chart", "figure"),
    Output("customer-frequency-chart", "figure"),
    Output("customer-recency-bands-chart", "figure"),
    Output("customer-monetary-bands-chart", "figure"),
    Output("customer-acquisition-chart", "figure"),
    Input("customer-highlight", "value")
)
def update_customer_additional_charts(selected_segment):
    return build_customer_additional_figures(selected_segment)
