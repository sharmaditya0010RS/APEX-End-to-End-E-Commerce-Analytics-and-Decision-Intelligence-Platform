import numpy as np
import plotly.graph_objects as go

from decision_data import (
    decision_evidence,
    selected_scenario,
    CAPACITIES,
    EFFECTIVENESS,
    COSTS,
    VALUES
)

BG = "#FFFFFF"
TEXT = "#17263D"
MUTED = "#52657E"
CYAN = "#42b9ff"
TEAL = "#36d2bb"
CORAL = "#f28d9b"
VIOLET = "#a58bff"
AMBER = "#ffb86b"
GRID = "#E8EDF5"


def finish(fig, height=330, left=65, bottom=52):
    fig.update_layout(
        title=None,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        height=height,
        font={"family": "Segoe UI, Arial", "color": TEXT},
        margin={"l": left, "r": 25, "t": 14, "b": bottom},
        hoverlabel={"bgcolor": "#FFFFFF", "font_size": 12},
        showlegend=False
    )
    fig.update_xaxes(automargin=True, zeroline=False)
    fig.update_yaxes(automargin=True, gridcolor=GRID, zeroline=False)
    return fig


def zero(fig):
    fig.add_hline(y=0, line_dash="dot", line_color=MUTED)
    return fig


def build_decision_figures(capacity=5, effectiveness=0.25, cost=5, value=50):
    data = decision_evidence()
    df = data["scenarios"]
    reference = data["break_even"].sort_values("review_budget_pct")
    selected = selected_scenario(data, capacity, effectiveness, cost, value)

    capacity = int(capacity)
    effectiveness = float(effectiveness)
    cost = float(cost)
    value = float(value)

    scope = df.loc[
        np.isclose(df["assumed_intervention_effectiveness"], effectiveness)
        & np.isclose(df["assumed_review_cost_brl"], cost)
        & np.isclose(df["assumed_value_per_prevented_late_brl"], value)
    ].sort_values("review_budget_pct")

    fixed_capacity = scope.loc[
        np.isclose(scope["review_budget_pct"], capacity)
    ].iloc[0]

    figures = []

    fig = go.Figure(go.Histogram(
        x=df["model_scenario_net_brl"],
        nbinsx=24,
        marker_color=CYAN,
        hovertemplate="Hypothetical net: R$%{x:,.0f}<br>Scenarios: %{y}<extra></extra>"
    ))
    finish(fig)
    fig.add_vline(x=0, line_color=CORAL, line_dash="dash")
    fig.add_vline(x=float(selected["model_scenario_net_brl"]), line_color=AMBER)
    fig.update_xaxes(title="Scenario model net value (R$)")
    fig.update_yaxes(title="Scenario combinations")
    figures.append(fig)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Assumed benefit", "Review expense", "Net value"],
        y=[
            float(selected["observed_model_late_identified"]) * effectiveness * value,
            -float(selected["scenario_review_expense_brl"]),
            float(selected["model_scenario_net_brl"])
        ],
        marker_color=[TEAL, CORAL, AMBER],
        hovertemplate="%{x}<br>R$%{y:+,.2f}<extra></extra>"
    ))
    finish(fig)
    zero(fig)
    fig.update_yaxes(title="Hypothetical BRL")
    figures.append(fig)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=scope["review_budget_pct"],
        y=scope["model_scenario_net_brl"],
        name="Model-ranked",
        mode="lines+markers",
        line={"color": CYAN, "width": 3},
        hovertemplate="%{x:g}% review<br>Net: R$%{y:+,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=scope["review_budget_pct"],
        y=scope["random_scenario_net_brl"],
        name="Random expected",
        mode="lines+markers",
        line={"color": VIOLET, "dash": "dash"},
        hovertemplate="%{x:g}% review<br>Net: R$%{y:+,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[capacity],
        y=[float(fixed_capacity["model_scenario_net_brl"])],
        mode="markers",
        name="Selected",
        marker={"size": 14, "color": AMBER},
        hovertemplate="%{x:g}% selected<br>R$%{y:+,.2f}<extra></extra>"
    ))
    finish(fig, bottom=80)
    zero(fig)
    fig.update_layout(
        showlegend=True,
        legend={"orientation": "h", "y": -0.24}
    )
    fig.update_xaxes(title="Review capacity (%)")
    fig.update_yaxes(title="Scenario net value (R$)")
    figures.append(fig)

    def sensitivity(dimension, values, multiplier, label):
        subset = df.loc[
            np.isclose(df["review_budget_pct"], capacity)
        ].copy()
        conditions = {
            "assumed_intervention_effectiveness": effectiveness,
            "assumed_review_cost_brl": cost,
            "assumed_value_per_prevented_late_brl": value
        }
        for column, required in conditions.items():
            if column != dimension:
                subset = subset.loc[np.isclose(subset[column], required)]
        subset = subset.sort_values(dimension)
        assert len(subset) == len(values)

        fig = go.Figure(go.Bar(
            x=[f"{float(v) * multiplier:g}" for v in subset[dimension]],
            y=subset["model_scenario_net_brl"],
            marker_color=[
                AMBER if np.isclose(v, conditions[dimension]) else TEAL
                for v in subset[dimension]
            ],
            hovertemplate=label + ": %{x}<br>Net: R$%{y:+,.2f}<extra></extra>"
        ))
        finish(fig)
        zero(fig)
        fig.update_xaxes(title=label)
        fig.update_yaxes(title="Scenario net (R$)")
        return fig

    figures.append(sensitivity(
        "assumed_review_cost_brl", COSTS, 1, "Review cost (R$)"
    ))
    figures.append(sensitivity(
        "assumed_intervention_effectiveness",
        EFFECTIVENESS, 100, "Effectiveness (%)"
    ))
    figures.append(sensitivity(
        "assumed_value_per_prevented_late_brl",
        VALUES, 1, "Value per prevention (R$)"
    ))

    break_even_rows = df.loc[
        np.isclose(df["assumed_intervention_effectiveness"], effectiveness)
        & np.isclose(df["assumed_review_cost_brl"], cost)
        & np.isclose(df["assumed_value_per_prevented_late_brl"], value)
    ].sort_values("review_budget_pct")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=break_even_rows["review_budget_pct"],
        y=break_even_rows["break_even_value_per_prevention_brl"],
        mode="lines+markers",
        line={"color": CORAL, "width": 3},
        name="Required break-even value",
        hovertemplate="%{x:g}% capacity<br>Required: R$%{y:,.2f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=CAPACITIES,
        y=[value] * len(CAPACITIES),
        mode="lines",
        line={"color": TEAL, "dash": "dash"},
        name="Assumed value",
        hovertemplate="Assumed: R$%{y:,.2f}<extra></extra>"
    ))
    finish(fig, bottom=78)
    fig.update_layout(showlegend=True, legend={"orientation": "h", "y": -0.24})
    fig.update_xaxes(title="Review capacity (%)")
    fig.update_yaxes(title="Value per prevented late (R$)")
    figures.append(fig)

    fig = go.Figure(go.Bar(
        x=[f"{float(v):g}%" for v in reference["review_budget_pct"]],
        y=reference["model_scenario_net_brl"],
        marker_color=CORAL,
        customdata=reference[["break_even_prevention_value_brl"]].to_numpy(),
        hovertemplate=(
            "Reference capacity: %{x}<br>Net: R$%{y:+,.2f}"
            "<br>Required value: R$%{customdata[0]:,.2f}<extra></extra>"
        )
    ))
    finish(fig)
    zero(fig)
    fig.update_yaxes(title="Documented reference net (R$)")
    figures.append(fig)

    fig = go.Figure(go.Bar(
        x=[f"{float(v):g}%" for v in scope["review_budget_pct"]],
        y=scope["model_incremental_vs_random_brl"],
        marker_color=VIOLET,
        hovertemplate="%{x} capacity<br>Model minus random: R$%{y:+,.2f}<extra></extra>"
    ))
    finish(fig)
    zero(fig)
    fig.update_yaxes(title="Incremental hypothetical value (R$)")
    figures.append(fig)

    grid = df.loc[
        np.isclose(df["review_budget_pct"], capacity)
        & np.isclose(df["assumed_intervention_effectiveness"], effectiveness)
    ]
    matrix = np.array([
        [
            float(grid.loc[
                np.isclose(grid["assumed_review_cost_brl"], c)
                & np.isclose(grid["assumed_value_per_prevented_late_brl"], v),
                "model_scenario_net_brl"
            ].iloc[0])
            for v in VALUES
        ]
        for c in COSTS
    ])

    fig = go.Figure(go.Heatmap(
        x=[f"R${v}" for v in VALUES],
        y=[f"R${c}" for c in COSTS],
        z=matrix,
        colorscale=[
            [0, "#df667d"],
            [0.5, "#293b52"],
            [1, "#36d2bb"]
        ],
        zmid=0,
        text=[[f"{v:+,.0f}" for v in row] for row in matrix],
        texttemplate="%{text}",
        textfont={"size": 14},
        colorbar={"title": {"text": "Net R$"}, "thickness": 12},
        hovertemplate=(
            "Assumed value: %{x}<br>Review cost: %{y}"
            "<br>Net: R$%{z:+,.2f}<extra></extra>"
        )
    ))
    finish(fig, height=410, left=95, bottom=75)
    fig.update_xaxes(title="Assumed value per prevention")
    fig.update_yaxes(title="Assumed review cost", autorange="reversed")
    figures.append(fig)

    assert len(figures) == 10
    return tuple(figures)
