from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "src" / "dashboard"))

from app import app

app._setup_server()

ids = [
    "customer-repeat-chart",
    "customer-average-value-chart",
    "customer-recency-segment-chart",
    "customer-frequency-chart",
    "customer-recency-bands-chart",
    "customer-monetary-bands-chart",
    "customer-acquisition-chart"
]

matches = [
    name for name in app.callback_map
    if all(graph_id in name for graph_id in ids)
]

assert len(matches) == 1, matches

payload = {
    "output": matches[0],
    "outputs": [
        {"id": graph_id, "property": "figure"}
        for graph_id in ids
    ],
    "inputs": [
        {"id": "customer-highlight", "property": "value", "value": "all"}
    ],
    "state": [],
    "changedPropIds": ["customer-highlight.value"]
}

client = app.server.test_client()
response = client.post("/_dash-update-component", json=payload)

print("HTTP STATUS:", response.status_code)

if response.status_code != 200:
    print(response.get_data(as_text=True)[:4000])
    raise RuntimeError("Dash callback returned an error")

body = response.get_json()
figures = body.get("response", {})

for graph_id in ids:
    result = figures.get(graph_id, {}).get("figure")
    assert result is not None, f"Missing figure: {graph_id}"
    assert len(result.get("data", [])) > 0, graph_id

    print(
        f"{graph_id}: PASS | "
        f"traces={len(result['data'])}"
    )

print("SEVEN FIGURES DELIVERED THROUGH DASH HTTP CALLBACK: PASS")
