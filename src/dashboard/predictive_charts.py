import numpy as np
import plotly.graph_objects as go

from predictive_data import predictive_evidence

BG = "#FFFFFF"
TEXT = "#17263D"
MUTED = "#52657E"
GRID = "#E8EDF5"
CYAN = "#42b9ff"
TEAL = "#36d2bb"
CORAL = "#f28d9b"
VIOLET = "#a58bff"
AMBER = "#ffb86b"

METRICS = [
    ("validation_average_precision", "Average precision", CYAN),
    ("validation_roc_auc", "ROC-AUC", TEAL),
    ("validation_brier_score", "Brier score", VIOLET)
]

CAPACITIES = [1, 5, 10, 20, 50, 100]


def finish(fig, height=330, left=58, bottom=48):
    fig.update_layout(
        title=None,
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font={"family": "Segoe UI, Arial", "color": TEXT},
        height=height,
        margin={"l": left, "r": 24, "t": 12, "b": bottom},
        hoverlabel={"bgcolor": "#FFFFFF", "font_size": 12},
        showlegend=False
    )
    fig.update_xaxes(
        automargin=True,
        title=None,
        tickfont={"size": 11, "color": MUTED},
        zeroline=False
    )
    fig.update_yaxes(
        automargin=True,
        title=None,
        tickfont={"size": 11, "color": MUTED},
        gridcolor=GRID,
        zeroline=False
    )
    return fig


def build_predictive_figures(highlight="expanded_logistic", capacity=5):
    evidence = predictive_evidence()
    board = evidence["leaderboard"].copy()
    budgets = evidence["budgets"].copy()
    calibration = evidence["calibration"].copy()
    monthly = evidence["monthly"].copy()
    test = evidence["test"]
    selection = evidence["selection"]

    if highlight not in set(board["model"]):
        raise ValueError("Invalid model highlight")

    capacity = int(capacity)
    if capacity not in CAPACITIES:
        raise ValueError("Invalid review capacity")

    figures = []

    for metric, label, main_color in METRICS:
        ranked = board.sort_values(metric, ascending=True)
        colors = [
            main_color if model == highlight else "#37516e"
            for model in ranked["model"]
        ]

        fig = go.Figure(go.Bar(
            x=ranked[metric],
            y=ranked["model"],
            orientation="h",
            marker_color=colors,
            hovertemplate=(
                "%{y}<br>" + label + ": %{x:.5f}<extra></extra>"
            )
        ))
        finish(fig, left=185)
        fig.update_yaxes(showgrid=False, ticks="", automargin=True)
        fig.update_xaxes(showgrid=True)
        figures.append(fig)

    validation_row = board.loc[
        board["model"].eq(selection["selected_model"])
    ].iloc[0]

    fig = go.Figure()
    for name, key_validation, key_test, color in [
        (
            "Average precision",
            "validation_average_precision",
            "test_average_precision",
            CYAN
        ),
        (
            "ROC-AUC",
            "validation_roc_auc",
            "test_roc_auc",
            VIOLET
        )
    ]:
        fig.add_trace(go.Bar(
            x=["Validation", "Held-out test"],
            y=[float(validation_row[key_validation]), float(test[key_test])],
            name=name,
            marker_color=color,
            hovertemplate="%{fullData.name}<br>%{x}: %{y:.4f}<extra></extra>"
        ))
    finish(fig)
    fig.update_layout(
        barmode="group",
        showlegend=True,
        legend={
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": -0.16
        },
        margin={"l": 57, "r": 22, "t": 12, "b": 75}
    )
    figures.append(fig)

    confusion = [
        [int(test["true_negative"]), int(test["false_positive"])],
        [int(test["false_negative"]), int(test["true_positive"])]
    ]
    matrix = go.Figure(go.Heatmap(
        z=confusion,
        x=["Predicted on time", "Predicted late"],
        y=["Actually on time", "Actually late"],
        colorscale=[
            [0, "#1e3450"], [0.5, "#277da0"], [1, "#38ccb8"]
        ],
        showscale=False,
        text=[[f"{v:,}" for v in row] for row in confusion],
        texttemplate="%{text}",
        textfont={"size": 17, "color": TEXT},
        hovertemplate="%{y}<br>%{x}<br>Orders: %{z:,}<extra></extra>"
    ))
    finish(matrix, left=112, bottom=76)
    matrix.update_yaxes(autorange="reversed", showgrid=False)
    figures.append(matrix)

    x_budget = budgets["review_budget_pct"].tolist()
    y_capture = (budgets["late_capture_rate"] * 100).tolist()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0] + x_budget,
        y=[0] + y_capture,
        mode="lines+markers",
        line={"color": CYAN, "width": 3},
        name="Model-ranked review",
        hovertemplate="%{x:g}% reviewed<br>%{y:.2f}% captured<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode="lines",
        line={"color": MUTED, "dash": "dash"},
        name="Random-review expectation"
    ))
    selected = budgets.loc[
        budgets["review_budget_pct"].eq(capacity)
    ].iloc[0]
    fig.add_trace(go.Scatter(
        x=[capacity],
        y=[float(selected["late_capture_rate"]) * 100],
        mode="markers",
        marker={
            "size": 16,
            "color": AMBER,
            "line": {"color": BG, "width": 2}
        },
        name="Selected capacity",
        hovertemplate="Selected: %{x:g}%<br>Capture: %{y:.2f}%<extra></extra>"
    ))
    finish(fig)
    fig.update_layout(
        showlegend=True,
        legend={"orientation": "h", "y": -0.2, "font": {"size": 10}},
        margin={"l": 58, "r": 24, "t": 12, "b": 92}
    )
    fig.update_xaxes(title="Review budget (%)", range=[0, 102])
    fig.update_yaxes(title="Late-order capture (%)", range=[0, 105])
    figures.append(fig)

    precision_values = (budgets["precision"] * 100).tolist()
    fig = go.Figure(go.Bar(
        x=[str(int(v)) + "%" for v in x_budget],
        y=precision_values,
        marker_color=[
            AMBER if int(v) == capacity else TEAL
            for v in x_budget
        ],
        hovertemplate="%{x} capacity<br>Precision: %{y:.2f}%<extra></extra>"
    ))
    finish(fig)
    fig.add_hline(
        y=float(test["test_late_rate"]) * 100,
        line_dash="dash",
        line_color=MUTED,
        annotation_text="Test prevalence",
        annotation_font_color=MUTED
    )
    fig.update_yaxes(title="Precision (%)", rangemode="tozero")
    figures.append(fig)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode="lines",
        line={"color": MUTED, "dash": "dash"},
        name="Perfect calibration"
    ))
    fig.add_trace(go.Scatter(
        x=calibration["predicted_probability"],
        y=calibration["observed_late_rate"],
        mode="lines+markers",
        line={"color": CORAL, "width": 3},
        marker={"size": 8},
        customdata=calibration[["observations"]].to_numpy(),
        name="Observed deciles",
        hovertemplate=(
            "Predicted: %{x:.2%}<br>"
            "Observed: %{y:.2%}<br>"
            "Orders: %{customdata[0]:,}<extra></extra>"
        )
    ))
    finish(fig)
    fig.update_xaxes(title="Mean predicted probability", tickformat=".0%")
    fig.update_yaxes(title="Observed late rate", tickformat=".0%")
    figures.append(fig)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly["purchase_month"],
        y=monthly["actual_late_rate"] * 100,
        marker_color=TEAL,
        name="Actual",
        hovertemplate="%{x}<br>Actual: %{y:.2f}%<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=monthly["purchase_month"],
        y=monthly["mean_predicted_risk"] * 100,
        marker_color=VIOLET,
        name="Predicted",
        hovertemplate="%{x}<br>Predicted: %{y:.2f}%<extra></extra>"
    ))
    finish(fig)
    fig.update_layout(
        barmode="group",
        showlegend=True,
        legend={"orientation": "h", "y": -0.17},
        margin={"l": 60, "r": 20, "t": 12, "b": 78}
    )
    fig.update_yaxes(title="Order rate (%)", rangemode="tozero")
    figures.append(fig)

    gap = (
        monthly["mean_predicted_risk"]
        - monthly["actual_late_rate"]
    ) * 100
    fig = go.Figure(go.Bar(
        x=monthly["purchase_month"],
        y=gap,
        marker_color=CORAL,
        customdata=monthly[["orders"]].to_numpy(),
        hovertemplate=(
            "%{x}<br>Predicted minus actual: %{y:+.2f} pp"
            "<br>Orders: %{customdata[0]:,}<extra></extra>"
        )
    ))
    finish(fig)
    fig.add_hline(y=0, line_color=MUTED, line_dash="dash")
    fig.update_yaxes(title="Percentage-point gap")
    figures.append(fig)

    if len(figures) != 10:
        raise RuntimeError("Expected exactly ten predictive charts")

    return tuple(figures)
