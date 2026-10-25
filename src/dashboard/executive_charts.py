import plotly.graph_objects as go

from data_access import executive_monthly_trends

BACKGROUND = "#FFFFFF"
TEXT = "#17263D"
MUTED = "#52657E"
GRID = "#E8EDF5"
CYAN = "#42b9ff"
TEAL = "#36d2bb"
VIOLET = "#a58bff"

def style_figure(fig, title, subtitle, y_title):
    fig.update_layout(
        title={
            "text": f"{title}<br><span style='font-size:11px;color:#94abc5'>{subtitle}</span>",
            "font": {"size": 18, "color": TEXT},
            "x": 0.035,
            "y": 0.97
        },
        annotations=[],
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=BACKGROUND,
        font={"family": "Segoe UI, Arial", "color": TEXT},
        height=370,
        margin={"l": 65, "r": 25, "t": 110, "b": 65},
        hovermode="x unified",
        showlegend=False
    )

    fig.update_xaxes(
        showgrid=False,
        tickfont={"color": MUTED},
        title=None
    )

    fig.update_yaxes(
        gridcolor=GRID,
        zeroline=False,
        tickfont={"color": MUTED},
        title={"text": y_title, "font": {"color": MUTED}}
    )

    return fig

def build_executive_figures(start_date, end_date):
    rows = executive_monthly_trends(start_date, end_date)

    months = [__import__("datetime").date.fromisoformat(row["month"]) for row in rows]
    orders = [row["orders"] for row in rows]
    values = [row["gross_item_value"] for row in rows]
    late_rates = [row["late_rate_pct"] for row in rows]

    volume = go.Figure()
    volume.add_trace(go.Scatter(
        x=months,
        y=orders,
        mode="lines+markers",
        line={"color": CYAN, "width": 3},
        marker={"size": 7},
        fill="tozeroy",
        fillcolor="rgba(66,185,255,0.10)",
        hovertemplate="%{x|%b %Y}: %{y:,} orders<extra></extra>"
    ))
    style_figure(
        volume,
        "01  /  Order Momentum",
        "Monthly purchased orders",
        "Orders"
    )

    monetary = go.Figure()
    monetary.add_trace(go.Bar(
        x=months,
        y=values,
        marker_color=TEAL,
        hovertemplate="%{x|%b %Y}: R$%{y:,.2f}<extra></extra>"
    ))
    style_figure(
        monetary,
        "02  /  Gross Item Value",
        "Monthly recorded merchandise value, excluding freight",
        "BRL"
    )
    monetary.update_yaxes(tickprefix="R$ ", tickformat="~s")

    sla = go.Figure()
    sla.add_trace(go.Scatter(
        x=months,
        y=late_rates,
        mode="lines+markers",
        line={"color": VIOLET, "width": 3},
        marker={"size": 8},
        hovertemplate="%{x|%b %Y}: %{y:.2f}% late<extra></extra>"
    ))
    style_figure(
        sla,
        "03  /  Delivery SLA Trend",
        "Calendar-date lateness among eligible delivered orders",
        "Late orders (%)"
    )
    sla.update_yaxes(ticksuffix="%")

    for figure in (volume, monetary, sla):
        figure.update_layout(
            title=None,
            annotations=[],
            height=330,
            margin={"l": 58, "r": 18, "t": 6, "b": 42}
        )
        figure.update_xaxes(automargin=True)
        figure.update_yaxes(automargin=True)

    return volume, monetary, sla

def build_executive_additional_figures(start_date, end_date):
    import datetime
    from data_access import executive_breakdowns

    breakdowns = executive_breakdowns(start_date, end_date)
    trend = executive_monthly_trends(start_date, end_date)

    status = breakdowns["status"]
    states = breakdowns["states"]
    monthly = breakdowns["monthly"]
    basket = breakdowns["basket"]

    figures = []

    fig = go.Figure(go.Pie(
        labels=[r["status"] for r in status],
        values=[r["orders"] for r in status],
        hole=0.67,
        sort=False,
        marker={"colors": [
            CYAN, TEAL, VIOLET, "#ffb86b", "#ef7192",
            "#7fc9b6", "#8296ff", "#d5aaff"
        ]},
        textinfo="none",
        hovertemplate="%{label}: %{value:,} orders (%{percent})<extra></extra>"
    ))
    style_figure(
        fig,
        "04  /  Order Status Composition",
        "Full status distribution for selected purchase dates",
        ""
    )
    fig.update_layout(
        showlegend=True,
        legend={"orientation": "h", "y": -0.13, "font": {"size": 10}},
        margin={"l": 24, "r": 24, "t": 100, "b": 100}
    )
    fig.add_annotation(
        x=0.5, y=0.5, xref="paper", yref="paper",
        text=f"{sum(r['orders'] for r in status):,}<br>orders",
        showarrow=False,
        font={"size": 17, "color": TEXT}
    )
    figures.append(fig)

    top_states = sorted(
        states, key=lambda r: r["orders"], reverse=True
    )[:10]
    top_states.reverse()

    fig = go.Figure(go.Bar(
        x=[r["orders"] for r in top_states],
        y=[r["state"] for r in top_states],
        orientation="h",
        marker_color=CYAN,
        hovertemplate="%{y}: %{x:,} orders<extra></extra>"
    ))
    style_figure(
        fig,
        "05  /  Top Customer States",
        "Highest order volumes by customer state",
        "Orders"
    )
    fig.update_layout(margin={"l": 65, "r": 25, "t": 110, "b": 60})
    figures.append(fig)

    by_value = sorted(
        states, key=lambda r: r["item_value"], reverse=True
    )[:10]
    by_value.reverse()

    fig = go.Figure(go.Bar(
        x=[r["item_value"] for r in by_value],
        y=[r["state"] for r in by_value],
        orientation="h",
        marker_color=TEAL,
        hovertemplate="%{y}: R$%{x:,.2f}<extra></extra>"
    ))
    style_figure(
        fig,
        "06  /  Geographic Merchandise Value",
        "Top customer states by gross recorded item value",
        "Gross item value (BRL)"
    )
    fig.update_xaxes(tickprefix="R$ ", tickformat="~s")
    figures.append(fig)

    month_dates = [
        datetime.date.fromisoformat(r["month"])
        for r in monthly
    ]
    averages = [
        r["item_value"] / r["orders"] if r["orders"] else None
        for r in monthly
    ]

    fig = go.Figure(go.Scatter(
        x=month_dates,
        y=averages,
        mode="lines+markers",
        line={"color": VIOLET, "width": 3},
        marker={"size": 7},
        hovertemplate="%{x|%b %Y}: R$%{y:,.2f}<extra></extra>"
    ))
    style_figure(
        fig,
        "07  /  Average Order Item Value",
        "Gross item value per purchased order, excluding freight",
        "BRL / order"
    )
    fig.update_yaxes(tickprefix="R$ ")
    figures.append(fig)

    freight_ratios = [
        100 * r["freight_value"] / r["item_value"]
        if r["item_value"] else None
        for r in monthly
    ]

    fig = go.Figure(go.Scatter(
        x=month_dates,
        y=freight_ratios,
        mode="lines+markers",
        line={"color": "#ffb86b", "width": 3},
        marker={"size": 7},
        fill="tozeroy",
        fillcolor="rgba(255,184,107,0.09)",
        hovertemplate="%{x|%b %Y}: %{y:.2f}%<extra></extra>"
    ))
    style_figure(
        fig,
        "08  /  Freight-to-Item-Value Ratio",
        "Recorded freight as a percentage of gross item value",
        "Freight / item value (%)"
    )
    fig.update_yaxes(ticksuffix="%")
    figures.append(fig)

    order_groups = [
        "1 item", "2 items", "3 items",
        "4–5 items", "6+ items", "Unknown"
    ]
    basket_counts = {r["group"]: r["orders"] for r in basket}
    visible_groups = [
        group for group in order_groups
        if basket_counts.get(group, 0) > 0
    ]

    fig = go.Figure(go.Bar(
        x=visible_groups,
        y=[basket_counts[group] for group in visible_groups],
        marker_color=[
            CYAN, TEAL, VIOLET, "#ffb86b", "#ef7192", "#8296ff"
        ][:len(visible_groups)],
        hovertemplate="%{x}: %{y:,} orders<extra></extra>"
    ))
    style_figure(
        fig,
        "09  /  Order Basket Size",
        "Recorded item-count distribution per purchased order",
        "Orders"
    )
    figures.append(fig)

    outcome_dates = [
        datetime.date.fromisoformat(r["month"])
        for r in trend
    ]
    ontime = [
        r["eligible_orders"] - r["late_orders"]
        for r in trend
    ]
    late = [r["late_orders"] for r in trend]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=outcome_dates,
        y=ontime,
        name="On time",
        marker_color=TEAL,
        hovertemplate="%{x|%b %Y}: %{y:,} on time<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=outcome_dates,
        y=late,
        name="Late",
        marker_color="#ef7192",
        hovertemplate="%{x|%b %Y}: %{y:,} late<extra></extra>"
    ))
    style_figure(
        fig,
        "10  /  Delivery Outcome Trend",
        "Calendar-date outcomes among SLA-eligible orders",
        "Eligible orders"
    )
    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend={"orientation": "h", "y": -0.18}
    )
    figures.append(fig)

    if len(figures) != 7:
        raise RuntimeError("Expected seven additional executive visuals")

    donut = figures[0]
    donut.update_layout(
        height=430,
        margin={"l": 30, "r": 30, "t": 88, "b": 115},
        legend={
            "orientation": "h",
            "y": -0.16,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 11, "color": MUTED}
        },
        annotations=[
            {
                "x": 0.5,
                "y": 0.5,
                "xref": "paper",
                "yref": "paper",
                "text": f"<b>{sum(r['orders'] for r in status):,}</b><br>orders",
                "showarrow": False,
                "font": {"size": 17, "color": TEXT}
            }
        ]
    )
    donut.update_traces(
        textinfo="none",
        hoverinfo="label+value+percent",
        domain={"x": [0.12, 0.88], "y": [0.03, 0.98]}
    )

    for index in [1, 2]:
        chart = figures[index]
        chart.update_layout(
            height=410,
            margin={"l": 55, "r": 42, "t": 86, "b": 48}
        )
        chart.update_yaxes(
            title_text=None,
            automargin=True,
            tickfont={"size": 12, "color": MUTED},
            showgrid=False
        )
        chart.update_xaxes(
            title_text=None,
            automargin=True,
            gridcolor=GRID,
            tickfont={"size": 11, "color": MUTED}
        )
        chart.update_traces(
            marker_line_width=0,
            opacity=0.94
        )

    figures[3].update_layout(height=390)
    figures[4].update_layout(height=390)
    figures[5].update_layout(height=390)
    figures[6].update_layout(
        height=400,
        margin={"l": 65, "r": 34, "t": 85, "b": 85}
    )

    for figure in figures:
        figure.update_layout(
            title=None,
            height=330,
            margin={"l": 58, "r": 18, "t": 6, "b": 42}
        )
        figure.update_xaxes(automargin=True)
        figure.update_yaxes(automargin=True)

    donut = figures[0]
    donut.update_layout(
        height=330,
        margin={"l": 10, "r": 10, "t": 0, "b": 82},
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.10,
            "yanchor": "top",
            "font": {"size": 10, "color": MUTED}
        },
        annotations=[
            {
                "x": 0.5,
                "y": 0.5,
                "xref": "paper",
                "yref": "paper",
                "text": f"<b>{sum(r['orders'] for r in status):,}</b><br>orders",
                "showarrow": False,
                "font": {"size": 17, "color": TEXT}
            }
        ]
    )
    donut.update_traces(
        textinfo="none",
        domain={"x": [0.12, 0.88], "y": [0.10, 0.96]}
    )

    for index in (1, 2):
        figure = figures[index]
        figure.update_layout(
            height=330,
            margin={"l": 90, "r": 20, "t": 8, "b": 44}
        )
        figure.update_yaxes(
            title_text=None,
            automargin=True,
            ticks="",
            tickfont={"size": 12, "color": MUTED},
            showgrid=False
        )
        figure.update_xaxes(
            title_text=None,
            automargin=True,
            tickfont={"size": 11, "color": MUTED},
            zeroline=False,
            showline=False
        )

    figures[6].update_layout(
        showlegend=True,
        height=330,
        margin={"l": 58, "r": 18, "t": 6, "b": 72},
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.17
        }
    )

    return tuple(figures)
