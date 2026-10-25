from pathlib import Path

import dash
from dash import Dash, dcc, html

BASE = Path(__file__).resolve().parent

app = Dash(
    __name__,
    use_pages=True,
    pages_folder=str(BASE / "pages"),
    assets_folder=str(BASE / "assets"),
    title="APEX Intelligence | Commerce Analytics",
    suppress_callback_exceptions=True
)

server = app.server

navigation = [
    ("01", "Executive Command", "/"),
    ("02", "Customer Intelligence", "/customers"),
    ("03", "Operations & Logistics", "/operations"),
    ("04", "Predictive Intelligence", "/predictive"),
    ("05", "Decision Scenario Lab", "/decisions")
]

sidebar = html.Aside(
    [
        html.Div(
            [
                html.Div("A", className="brand-mark"),
                html.Div(
                    [
                        html.Div("APEX", className="brand-name"),
                        html.Div("INTELLIGENCE PLATFORM", className="brand-caption")
                    ]
                )
            ],
            className="brand"
        ),
        html.Div("WORKSPACES", className="nav-label"),
        html.Nav(
            [
                dcc.Link(
                    [
                        html.Span(number, className="nav-number"),
                        html.Span(label)
                    ],
                    href=path,
                    className="nav-link"
                )
                for number, label, path in navigation
            ]
        ),
        html.Div(
            [
                html.Div("DATA INTEGRITY", className="sidebar-foot-label"),
                html.Div(
                    [
                        html.Span(className="status-dot"),
                        html.Span("Historical Olist Warehouse")
                    ],
                    className="sidebar-status"
                ),
                html.Div(
                    "Research analytics · Not a live operational feed",
                    className="sidebar-foot-note"
                )
            ],
            className="sidebar-footer"
        )
    ],
    className="sidebar"
)

app.layout = html.Div(
    [
        sidebar,
        html.Main(
            [
                html.Header(
                    [
                        html.Div(
                            [
                                html.Div(
                                    "COMMERCE ANALYTICS / PROJECT APEX",
                                    className="topbar-eyebrow"
                                ),
                                html.Div(
                                    "Decision Intelligence Workspace",
                                    className="topbar-title"
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.Span(className="status-dot"),
                                html.Span("Historical data")
                            ],
                            className="topbar-status"
                        )
                    ],
                    className="topbar"
                ),
                html.Div(dash.page_container, className="page-content")
            ],
            className="main-panel"
        )
    ],
    className="app-shell"
)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8050, debug=False)
