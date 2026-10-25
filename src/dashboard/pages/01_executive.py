import dash
from dash import Input, Output, dcc, html

from data_access import executive_kpis
from executive_charts import build_executive_figures, build_executive_additional_figures

dash.register_page(
    __name__,
    path="/",
    name="Executive Command",
    order=0
)

def metric_card(label, value, detail):
    return html.Div(
        [
            html.Div(label, className="metric-label"),
            html.Div(value, className="metric-value"),
            html.Div(detail, className="metric-detail")
        ],
        className="metric-card"
    )

CHART_DETAILS = {
    "executive-order-momentum": ("01", "Order Momentum", "Monthly purchased orders"),
    "executive-gross-value": ("02", "Gross Item Value", "Recorded merchandise value excluding freight"),
    "executive-sla-trend": ("03", "Delivery SLA Trend", "Calendar-date lateness among eligible orders"),
    "executive-status-composition": ("04", "Order Status Composition", "Purchase-period order status distribution"),
    "executive-top-states": ("05", "Top Customer States", "Top states ranked by order volume"),
    "executive-geographic-value": ("06", "Geographic Merchandise Value", "Customer states ranked by gross item value"),
    "executive-average-order-value": ("07", "Average Order Item Value", "Gross item value per purchased order"),
    "executive-freight-ratio": ("08", "Freight-to-Item-Value Ratio", "Monthly freight relative to item value"),
    "executive-basket-size": ("09", "Order Basket Size", "Distribution of recorded items per order"),
    "executive-delivery-outcomes": ("10", "Delivery Outcome Trend", "On-time versus late eligible orders")
}

def graph_card(graph_id, wide=False):
    number, title, subtitle = CHART_DETAILS[graph_id]

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
                        style={"height": "330px", "width": "100%"},
                        config={
                            "displaylogo": False,
                            "scrollZoom": False,
                            "responsive": True
                        }
                    ),
                    type="circle"
                ),
                className="chart-body"
            )
        ],
        className="apex-graph-card apex-graph-wide" if wide else "apex-graph-card"
    )

def layout(**kwargs):
    kpi = executive_kpis()

    return html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "01 / EXECUTIVE INTELLIGENCE",
                                className="eyebrow"
                            ),
                            html.H1("Executive Command Center"),
                            html.P(
                                "Historical marketplace trends, merchandise value and delivery reliability.",
                                className="page-description"
                            )
                        ]
                    ),
                    html.Div(
                        "VERIFIED WAREHOUSE DATA",
                        className="data-pill"
                    )
                ],
                className="page-heading"
            ),
            html.Div(
                [
                    metric_card(
                        "TOTAL ORDERS",
                        f"{kpi['total_orders']:,}",
                        "Full historical dataset"
                    ),
                    metric_card(
                        "DISTINCT CUSTOMERS",
                        f"{kpi['unique_customers']:,}",
                        "Unique customer identities"
                    ),
                    metric_card(
                        "GROSS ITEM VALUE",
                        f"R$ {kpi['gross_item_value'] / 1_000_000:,.2f}M",
                        "All recorded item value, excluding freight"
                    ),
                    metric_card(
                        "LATE DELIVERY RATE",
                        f"{kpi['late_rate']:.2%}",
                        f"{kpi['late_orders']:,} / {kpi['eligible_orders']:,} eligible"
                    )
                ],
                className="metric-grid"
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "INTERACTIVE ANALYSIS",
                                className="eyebrow"
                            ),
                            html.H2("Marketplace Trends"),
                            html.P(
                                "Change the purchase-date window to update all ten charts. KPI cards above display full-history totals.",
                                className="page-description"
                            )
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                "PURCHASE DATE RANGE",
                                className="filter-label"
                            ),
                            dcc.DatePickerRange(
                                id="executive-date-range",
                                min_date_allowed="2017-01-01",
                                max_date_allowed="2018-08-31",
                                start_date="2017-01-01",
                                end_date="2018-08-31",
                                display_format="DD MMM YYYY",
                                clearable=False
                            )
                        ],
                        className="date-filter-wrap"
                    )
                ],
                className="analysis-toolbar"
            ),
            html.Div(
                [
                    graph_card("executive-order-momentum"),
                    graph_card("executive-gross-value"),
                    graph_card("executive-sla-trend", wide=True),
                    graph_card("executive-status-composition"),
                    graph_card("executive-top-states"),
                    graph_card("executive-geographic-value"),
                    graph_card("executive-average-order-value"),
                    graph_card("executive-freight-ratio"),
                    graph_card("executive-basket-size"),
                    graph_card("executive-delivery-outcomes", wide=True)
                ],
                className="apex-chart-grid"
            ),
            html.Div(
                "Source: historical Olist orders · Date filtering applies to purchased-order cohorts · No live operational feed",
                className="chart-footnote"
            )
        ]
    )

@dash.callback(
    Output("executive-order-momentum", "figure"),
    Output("executive-gross-value", "figure"),
    Output("executive-sla-trend", "figure"),
    Output("executive-status-composition", "figure"),
    Output("executive-top-states", "figure"),
    Output("executive-geographic-value", "figure"),
    Output("executive-average-order-value", "figure"),
    Output("executive-freight-ratio", "figure"),
    Output("executive-basket-size", "figure"),
    Output("executive-delivery-outcomes", "figure"),
    Input("executive-date-range", "start_date"),
    Input("executive-date-range", "end_date")
)
def update_executive_charts(start_date, end_date):
    first_three = build_executive_figures(start_date, end_date)
    remaining_seven = build_executive_additional_figures(start_date, end_date)
    return (*first_three, *remaining_seven)
