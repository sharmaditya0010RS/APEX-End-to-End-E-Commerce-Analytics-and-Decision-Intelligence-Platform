from pathlib import Path
import sys
import traceback

sys.path.insert(0, str(Path.cwd() / "src" / "dashboard"))

from predictive_data import predictive_evidence
from predictive_charts import build_predictive_figures
from app import app

def check(name, action):
    print(f"\nCHECK: {name}", flush=True)
    try:
        result = action()
        print(f"{name}: PASS", flush=True)
        return result
    except Exception:
        traceback.print_exc()
        sys.exit(1)

def inspect_evidence():
    data = predictive_evidence()

    for name in ["leaderboard", "budgets", "calibration", "monthly"]:
        frame = data[name]
        print(name, "rows:", len(frame))
        print(name, "columns:", list(frame.columns))

    print("TEST KEYS:", sorted(data["test"].keys()))
    print("SELECTION KEYS:", sorted(data["selection"].keys()))
    return data

def inspect_figures():
    figures = build_predictive_figures("expanded_logistic", 5)

    assert len(figures) == 10

    for number, figure in enumerate(figures, start=31):
        assert len(figure.data) >= 1
        assert len(figure.to_json()) > 300
        print(
            f"VISUAL {number}: {len(figure.data)} traces | "
            f"{figure.data[0].type}",
            flush=True
        )
    return figures

def inspect_http():
    app._setup_server()

    ids = [
        f"predictive-visual-{number}"
        for number in range(31, 41)
    ]

    matches = [
        key for key in app.callback_map
        if all(graph_id in key for graph_id in ids)
    ]

    assert len(matches) == 1, list(app.callback_map)

    payload = {
        "output": matches[0],
        "outputs": [
            {"id": graph_id, "property": "figure"}
            for graph_id in ids
        ],
        "inputs": [
            {
                "id": "predictive-model-filter",
                "property": "value",
                "value": "expanded_logistic"
            },
            {
                "id": "predictive-capacity-filter",
                "property": "value",
                "value": 5
            }
        ],
        "state": [],
        "changedPropIds": [
            "predictive-model-filter.value",
            "predictive-capacity-filter.value"
        ]
    }

    response = app.server.test_client().post(
        "/_dash-update-component",
        json=payload
    )

    print("HTTP STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.get_data(as_text=True)[:5000])
        raise RuntimeError("Predictive callback HTTP failure")

    body = response.get_json()["response"]

    for graph_id in ids:
        figure = body.get(graph_id, {}).get("figure")
        assert figure is not None, graph_id
        assert len(figure.get("data", [])) >= 1, graph_id
        print(f"{graph_id}: HTTP FIGURE PASS")

    return True

check("MODEL EVIDENCE", inspect_evidence)
check("TEN PLOTLY FIGURES", inspect_figures)
check("DASH HTTP CALLBACK", inspect_http)

print("\nPREDICTIVE BACKEND DIAGNOSTICS: ALL PASS")
