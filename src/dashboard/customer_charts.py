import plotly.graph_objects as go

from data_access import customer_intelligence_data

BG = "#FFFFFF"
TEXT = "#17263D"
MUTED = "#52657E"
CYAN = "#42b9ff"
TEAL = "#36d2bb"
VIOLET = "#a58bff"
GRID = "#E8EDF5"

def frame(fig, height=330):
    fig.update_layout(
        title=None,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font={"family": "Segoe UI, Arial", "color": TEXT},
        height=height,
        margin={"l": 18, "r": 22, "t": 12, "b": 46},
        hoverlabel={"bgcolor": "#FFFFFF", "font_size": 12},
        showlegend=False
    )
    return fig

def build_customer_figures(metric="customers", selected_segment="all", horizon=12):
    if metric not in {"customers", "orders"}:
        raise ValueError("Invalid customer metric")
    if horizon not in {3, 6, 12}:
        raise ValueError("Invalid cohort horizon")

    data = customer_intelligence_data()
    segments = data["segments"]
    cohorts = data["cohorts"]

    names = [r["segment"] for r in segments]
    if selected_segment != "all" and selected_segment not in names:
        raise ValueError("Invalid segment")

    ranked = sorted(segments, key=lambda r: r[metric])
    segment_colors = [
        CYAN if selected_segment in {"all", r["segment"]} else "#38536e"
        for r in ranked
    ]

    fig1 = go.Figure(go.Bar(
        x=[r[metric] for r in ranked],
        y=[r["segment"] for r in ranked],
        orientation="h",
        marker={"color": segment_colors},
        customdata=[r["segment"] for r in ranked],
        hovertemplate="%{customdata}<br>%{x:,.0f} " + metric + "<extra></extra>"
    ))
    frame(fig1)
    fig1.update_layout(margin={"l": 163, "r": 24, "t": 12, "b": 40})
    fig1.update_xaxes(gridcolor=GRID, zeroline=False, title=None)
    fig1.update_yaxes(ticks="", title=None, showgrid=False, automargin=True)

    total_value = sum(r["gross_value"] for r in segments)
    value_colors = [
        TEAL if selected_segment in {"all", r["segment"]} else "#38536e"
        for r in segments
    ]
    fig2 = go.Figure(go.Treemap(
        labels=names,
        parents=[""] * len(names),
        values=[r["gross_value"] for r in segments],
        marker={"colors": value_colors, "line": {"color": BG, "width": 3}},
        textinfo="label+percent root",
        textfont={"size": 12},
        hovertemplate="<b>%{label}</b><br>R$%{value:,.2f}<br>%{percentRoot:.1%} of total<extra></extra>",
        root={"color": BG}
    ))
    frame(fig2)
    fig2.update_layout(margin={"l": 8, "r": 8, "t": 8, "b": 8})

    cohort_names = sorted({r["cohort"] for r in cohorts})
    lookup = {
        (r["cohort"], r["month_offset"]): r
        for r in cohorts
    }
    offsets = list(range(horizon + 1))
    z = []
    hover = []

    for cohort in cohort_names:
        values = []
        descriptions = []
        for offset in offsets:
            row = lookup[(cohort, offset)]
            if row["observable"]:
                value = row["activity_pct"]
                descriptions.append(
                    f"Cohort: {cohort}<br>Month: M+{offset}"
                    f"<br>Active: {row['active_customers']:,}"
                    f" / {row['cohort_size']:,}"
                    f"<br>Purchase activity: {value:.3f}%"
                )
            else:
                value = None
                descriptions.append(
                    f"Cohort: {cohort}<br>Month: M+{offset}"
                    "<br>Not fully observable"
                )
            values.append(value)
        z.append(values)
        hover.append(descriptions)

    fig3 = go.Figure(go.Heatmap(
        x=offsets,
        y=cohort_names,
        z=z,
        customdata=hover,
        colorscale=[
            [0.0, "#172940"],
            [0.15, "#205d83"],
            [0.5, "#23a9bd"],
            [1.0, "#68efd3"]
        ],
        zmin=0,
        zmax=100,
        hoverongaps=False,
        hovertemplate="%{customdata}<extra></extra>",
        colorbar={
            "title": {"text": "%"},
            "thickness": 12,
            "len": 0.78,
            "tickfont": {"color": MUTED}
        },
        xgap=2,
        ygap=2
    ))
    frame(fig3, height=550)
    fig3.update_layout(
        margin={"l": 98, "r": 45, "t": 12, "b": 58},
        annotations=[
            {
                "text": "Blank cells = months without a complete observation window",
                "xref": "paper", "yref": "paper",
                "x": 0, "y": -0.13,
                "showarrow": False,
                "xanchor": "left",
                "font": {"size": 11, "color": MUTED}
            }
        ]
    )
    fig3.update_xaxes(
        title="Months since first delivered purchase",
        tickmode="array",
        tickvals=offsets,
        ticktext=[f"M+{i}" for i in offsets],
        tickfont={"size": 10, "color": MUTED}
    )
    fig3.update_yaxes(
        title=None,
        autorange="reversed",
        tickfont={"size": 10, "color": MUTED}
    )

    assert len(fig1.data) == len(fig2.data) == len(fig3.data) == 1
    assert abs(total_value - 13221498.11) < 0.02
    return fig1, fig2, fig3

def build_customer_additional_figures(selected_segment="all"):
    from datetime import date
    from data_access import customer_rfm_distributions

    data = customer_intelligence_data()
    segments = data["segments"]
    cohorts = data["cohorts"]

    names = {r["segment"] for r in segments}
    if selected_segment != "all" and selected_segment not in names:
        raise ValueError("Invalid customer segment")

    distributions = customer_rfm_distributions(selected_segment)
    total_customers = sum(r["customers"] for r in segments)

    repeat_customers = sum(
        r["customers"] for r in segments
        if "Repeat" in r["segment"] or r["segment"] == "Repeat Champions"
    )
    one_time_customers = total_customers - repeat_customers

    figures = []

    repeat_figure = go.Figure(go.Pie(
        labels=["One-time purchasers", "Repeat purchasers"],
        values=[one_time_customers, repeat_customers],
        hole=0.68,
        sort=False,
        marker={
            "colors": [CYAN, VIOLET],
            "line": {"color": BG, "width": 3}
        },
        textinfo="none",
        hovertemplate="%{label}<br>%{value:,} customers<br>%{percent}<extra></extra>"
    ))
    frame(repeat_figure)
    repeat_figure.update_layout(
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.10,
            "font": {"size": 11}
        },
        margin={"l": 15, "r": 15, "t": 8, "b": 70},
        annotations=[{
            "x": 0.5,
            "y": 0.5,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "text": f"<b>{repeat_customers / total_customers:.2%}</b><br>repeat",
            "font": {"size": 17, "color": TEXT}
        }]
    )
    figures.append(repeat_figure)

    def segment_ranking(field, color, unit):
        ordered = sorted(segments, key=lambda r: r[field])
        colors = [
            color if selected_segment in {"all", r["segment"]}
            else "#38536e"
            for r in ordered
        ]
        fig = go.Figure(go.Bar(
            x=[r[field] for r in ordered],
            y=[r["segment"] for r in ordered],
            orientation="h",
            marker_color=colors,
            hovertemplate="%{y}<br>%{x:,.2f} " + unit + "<extra></extra>"
        ))
        frame(fig)
        fig.update_layout(
            margin={"l": 172, "r": 25, "t": 8, "b": 42}
        )
        fig.update_xaxes(gridcolor=GRID, zeroline=False, title=None)
        fig.update_yaxes(
            ticks="",
            title=None,
            automargin=True,
            showgrid=False
        )
        return fig

    avg_value = segment_ranking("mean_value", TEAL, "BRL/customer")
    avg_value.update_xaxes(tickprefix="R$ ")
    figures.append(avg_value)

    avg_recency = segment_ranking("mean_recency", VIOLET, "days")
    figures.append(avg_recency)

    def distribution_figure(dimension, labels, color):
        counts = distributions[dimension]
        values = [counts.get(label, 0) for label in labels]

        fig = go.Figure(go.Bar(
            x=labels,
            y=values,
            marker_color=color,
            hovertemplate="%{x}<br>%{y:,} customers<extra></extra>"
        ))
        frame(fig)
        fig.update_layout(
            margin={"l": 63, "r": 20, "t": 8, "b": 65}
        )
        fig.update_xaxes(
            title=None,
            tickfont={"size": 11, "color": MUTED},
            tickangle=0
        )
        fig.update_yaxes(
            title=None,
            gridcolor=GRID,
            zeroline=False
        )
        return fig

    frequency_labels = [
        "1 order", "2 orders", "3 orders", "4+ orders"
    ]
    recency_labels = [
        "0–90 days", "91–180 days", "181–365 days", "366+ days"
    ]
    monetary_labels = [
        "Below R$50", "R$50–149", "R$150–499", "R$500+"
    ]

    figures.append(distribution_figure(
        "frequency", frequency_labels, CYAN
    ))
    figures.append(distribution_figure(
        "recency", recency_labels, VIOLET
    ))
    figures.append(distribution_figure(
        "monetary", monetary_labels, TEAL
    ))

    acquisition = sorted(
        (
            row for row in cohorts
            if row["month_offset"] == 0
        ),
        key=lambda row: row["cohort"]
    )

    cohort_figure = go.Figure(go.Bar(
        x=[date.fromisoformat(r["cohort"]) for r in acquisition],
        y=[r["cohort_size"] for r in acquisition],
        marker_color=CYAN,
        hovertemplate="%{x|%b %Y}<br>%{y:,} customers<extra></extra>"
    ))
    frame(cohort_figure)
    cohort_figure.update_layout(
        margin={"l": 65, "r": 25, "t": 8, "b": 50}
    )
    cohort_figure.update_xaxes(title=None)
    cohort_figure.update_yaxes(
        title=None,
        gridcolor=GRID,
        zeroline=False
    )
    figures.append(cohort_figure)

    assert len(figures) == 7
    return tuple(figures)
