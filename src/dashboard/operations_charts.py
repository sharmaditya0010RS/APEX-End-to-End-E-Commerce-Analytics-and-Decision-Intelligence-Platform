from datetime import date

import plotly.graph_objects as go

from data_access import operations_delivery_data

BG = "#FFFFFF"
TEXT = "#17263D"
MUTED = "#52657E"
GRID = "#E8EDF5"
CYAN = "#42b9ff"
TEAL = "#36d2bb"
VIOLET = "#a58bff"
CORAL = "#f28d9b"

DURATION_BANDS = [
    "Negative",
    "0–6 days",
    "7–13 days",
    "14–20 days",
    "21–29 days",
    "30–44 days",
    "45+ days"
]


def frame(figure, height=330):
    figure.update_layout(
        title=None,
        height=height,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font={"family": "Segoe UI, Arial", "color": TEXT},
        hoverlabel={"bgcolor": "#FFFFFF", "font_size": 12},
        margin={"l": 62, "r": 28, "t": 18, "b": 55},
        showlegend=False
    )
    figure.update_xaxes(
        automargin=True,
        tickfont={"size": 11, "color": MUTED},
        zeroline=False
    )
    figure.update_yaxes(
        automargin=True,
        tickfont={"size": 11, "color": MUTED},
        gridcolor=GRID,
        zeroline=False
    )
    return figure


def build_operations_figures(start_date, end_date, state="all"):
    data = operations_delivery_data(start_date, end_date, state)

    monthly = data["monthly"]
    duration = data["duration"]
    comparison = data["comparison"]

    if not monthly:
        raise ValueError("No eligible orders in the selected period")

    months = [date.fromisoformat(row["month"]) for row in monthly]
    rates = [
        100 * row["late"] / row["eligible"]
        for row in monthly
    ]

    sla = go.Figure(go.Scatter(
        x=months,
        y=rates,
        mode="lines+markers",
        line={"color": CYAN, "width": 3},
        marker={"size": 7},
        customdata=[
            [row["late"], row["eligible"]]
            for row in monthly
        ],
        hovertemplate=(
            "%{x|%b %Y}<br>"
            "Late rate: %{y:.2f}%<br>"
            "Late: %{customdata[0]:,}<br>"
            "Eligible: %{customdata[1]:,}<extra></extra>"
        )
    ))
    frame(sla)
    sla.update_yaxes(title=None, ticksuffix="%", rangemode="tozero")

    counts = {
        row["band"]: row["orders"]
        for row in duration
    }
    bands = [
        band for band in DURATION_BANDS
        if counts.get(band, 0) > 0
    ]

    histogram = go.Figure(go.Bar(
        x=bands,
        y=[counts[band] for band in bands],
        marker_color=[
            CORAL if band == "Negative" else TEAL
            for band in bands
        ],
        hovertemplate="%{x}<br>%{y:,} orders<extra></extra>"
    ))
    frame(histogram)
    histogram.update_layout(margin={"l": 64, "r": 22, "t": 18, "b": 76})
    histogram.update_xaxes(tickangle=-20, title=None)
    histogram.update_yaxes(title=None)

    bubble = go.Figure(go.Scatter(
        x=[row["promised_bin"] + 2.5 for row in comparison],
        y=[row["actual_bin"] + 2.5 for row in comparison],
        mode="markers",
        marker={
            "color": [row["orders"] for row in comparison],
            "colorscale": [
                [0, "#35668c"],
                [0.5, CYAN],
                [1, TEAL]
            ],
            "size": [
                7 + min(25, row["orders"] ** 0.40)
                for row in comparison
            ],
            "opacity": 0.8,
            "showscale": True,
            "colorbar": {
                "title": {"text": "Orders"},
                "thickness": 10,
                "tickfont": {"color": MUTED}
            },
            "line": {"color": BG, "width": 0.6}
        },
        customdata=[
            [row["orders"], row["promised_bin"], row["actual_bin"]]
            for row in comparison
        ],
        hovertemplate=(
            "Promised: %{customdata[1]}–%{customdata[1]}+5 days<br>"
            "Actual: %{customdata[2]}–%{customdata[2]}+5 days<br>"
            "Orders: %{customdata[0]:,}<extra></extra>"
        )
    ))
    frame(bubble, height=410)
    bubble.update_layout(
        margin={"l": 75, "r": 70, "t": 18, "b": 70}
    )
    bubble.update_xaxes(title="Promised delivery duration (days)")
    bubble.update_yaxes(title="Actual delivery duration (days)")

    return sla, histogram, bubble

def build_operations_additional_figures(start_date, end_date, state="all"):
    from datetime import date
    from data_access import operations_additional_data

    data = operations_additional_data(start_date, end_date, state)
    geography = data["geography"]
    monthly = data["monthly"]
    sellers = data["sellers"]
    reviews = data["reviews"]

    figures = []

    eligible_states = sorted(
        [r for r in geography if r["eligible"] >= 100],
        key=lambda r: 100 * r["late"] / r["eligible"]
    )[-12:]

    state_rates = [
        100 * r["late"] / r["eligible"]
        for r in eligible_states
    ]

    fig = go.Figure(go.Bar(
        x=state_rates,
        y=[r["state"] for r in eligible_states],
        orientation="h",
        marker_color=CORAL,
        customdata=[
            [r["late"], r["eligible"]] for r in eligible_states
        ],
        hovertemplate=(
            "%{y}<br>Late rate: %{x:.2f}%<br>"
            "Late: %{customdata[0]:,}<br>"
            "Eligible: %{customdata[1]:,}<extra></extra>"
        )
    ))
    frame(fig)
    fig.update_layout(margin={"l": 76, "r": 25, "t": 10, "b": 45})
    fig.update_xaxes(title=None, ticksuffix="%")
    fig.update_yaxes(title=None, ticks="", showgrid=False)
    figures.append(fig)

    month_dates = [date.fromisoformat(r["month"]) for r in monthly]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=month_dates,
        y=[r["on_time"] for r in monthly],
        name="On time",
        marker_color=TEAL,
        hovertemplate="%{x|%b %Y}<br>On time: %{y:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=month_dates,
        y=[r["late"] for r in monthly],
        name="Late",
        marker_color=CORAL,
        hovertemplate="%{x|%b %Y}<br>Late: %{y:,}<extra></extra>"
    ))
    frame(fig)
    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend={"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.2},
        margin={"l": 58, "r": 20, "t": 8, "b": 72}
    )
    figures.append(fig)

    freight_order = [
        "Below R$10", "R$10–19", "R$20–39",
        "R$40–79", "R$80+", "Missing"
    ]
    freight_counts = {r["band"]: r["orders"] for r in data["freight"]}

    fig = go.Figure(go.Bar(
        x=[r for r in freight_order if freight_counts.get(r, 0) > 0],
        y=[freight_counts[r] for r in freight_order if freight_counts.get(r, 0) > 0],
        marker_color=CYAN,
        hovertemplate="%{x}<br>%{y:,} orders<extra></extra>"
    ))
    frame(fig)
    fig.update_layout(margin={"l": 62, "r": 20, "t": 8, "b": 72})
    fig.update_yaxes(title=None)
    fig.update_xaxes(title=None, tickfont={"size": 10})
    figures.append(fig)

    freight_states = sorted(
        [
            {
                **r,
                "freight_pct": (
                    100 * r["freight_value"] / r["item_value"]
                )
            }
            for r in geography
            if r["eligible"] >= 100 and r["item_value"] > 0
        ],
        key=lambda r: r["freight_pct"]
    )[-12:]

    fig = go.Figure(go.Bar(
        x=[r["freight_pct"] for r in freight_states],
        y=[r["state"] for r in freight_states],
        orientation="h",
        marker_color=VIOLET,
        customdata=[[r["eligible"]] for r in freight_states],
        hovertemplate=(
            "%{y}<br>Freight / item value: %{x:.2f}%<br>"
            "Eligible orders: %{customdata[0]:,}<extra></extra>"
        )
    ))
    frame(fig)
    fig.update_layout(margin={"l": 76, "r": 25, "t": 10, "b": 45})
    fig.update_xaxes(title=None, ticksuffix="%")
    fig.update_yaxes(title=None, ticks="", showgrid=False)
    figures.append(fig)

    high_volume = sorted(
        sellers,
        key=lambda r: (r["seller_orders"], r["seller_id"]),
        reverse=True
    )[:12]
    high_volume.reverse()

    fig = go.Figure(go.Bar(
        x=[r["seller_orders"] for r in high_volume],
        y=[r["seller_id"][:8] for r in high_volume],
        orientation="h",
        marker_color=TEAL,
        customdata=[
            [r["seller_id"], r["eligible"]] for r in high_volume
        ],
        hovertemplate=(
            "Seller: %{customdata[0]}<br>"
            "Seller-order pairs: %{x:,}<br>"
            "SLA-eligible: %{customdata[1]:,}<extra></extra>"
        )
    ))
    frame(fig)
    fig.update_layout(margin={"l": 88, "r": 25, "t": 10, "b": 45})
    fig.update_yaxes(title=None, ticks="", showgrid=False)
    fig.update_xaxes(title=None)
    figures.append(fig)

    reliable_sample = sorted(
        [r for r in sellers if r["eligible"] >= 30],
        key=lambda r: (100 * r["late"] / r["eligible"], r["seller_id"])
    )[-12:]
    reliable_sample.reverse()

    fig = go.Figure(go.Bar(
        x=[100 * r["late"] / r["eligible"] for r in reliable_sample],
        y=[r["seller_id"][:8] for r in reliable_sample],
        orientation="h",
        marker_color=CORAL,
        customdata=[
            [r["seller_id"], r["late"], r["eligible"]]
            for r in reliable_sample
        ],
        hovertemplate=(
            "Seller: %{customdata[0]}<br>"
            "Late rate: %{x:.2f}%<br>"
            "Late: %{customdata[1]:,}<br>"
            "Eligible: %{customdata[2]:,}<extra></extra>"
        )
    ))
    frame(fig)
    fig.update_layout(margin={"l": 88, "r": 25, "t": 10, "b": 45})
    fig.update_yaxes(title=None, ticks="", showgrid=False)
    fig.update_xaxes(title=None, ticksuffix="%")
    figures.append(fig)

    score_values = [1, 2, 3, 4, 5]
    lookup = {
        (r["late"], r["score"]): r["orders"]
        for r in reviews
    }

    fig = go.Figure()
    for is_late, name, color in [
        (False, "On time", TEAL),
        (True, "Late", CORAL)
    ]:
        fig.add_trace(go.Bar(
            x=score_values,
            y=[lookup.get((is_late, score), 0) for score in score_values],
            name=name,
            marker_color=color,
            hovertemplate=(
                "Rounded review score: %{x}<br>"
                + name + ": %{y:,} orders<extra></extra>"
            )
        ))
    frame(fig)
    fig.update_layout(
        barmode="group",
        showlegend=True,
        legend={"orientation": "h", "x": 0.5, "xanchor": "center", "y": -0.17},
        margin={"l": 62, "r": 20, "t": 10, "b": 72}
    )
    fig.update_xaxes(
        title="Rounded order-average review score",
        tickmode="array",
        tickvals=score_values
    )
    fig.update_yaxes(title=None)
    figures.append(fig)

    if len(figures) != 7:
        raise RuntimeError("Expected seven operations figures")

    return tuple(figures)
