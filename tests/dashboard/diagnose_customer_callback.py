from pathlib import Path
import sys
import traceback

root = Path.cwd()
sys.path.insert(0, str(root / "src" / "dashboard"))

from customer_charts import build_customer_additional_figures
from data_access import customer_rfm_distributions

try:
    print("CHECK 1: RFM AGGREGATIONS", flush=True)
    distributions = customer_rfm_distributions("all")

    for dimension, buckets in distributions.items():
        print(dimension, sum(buckets.values()), buckets, flush=True)

    print("CHECK 2: SEVEN PLOTLY FIGURES", flush=True)
    figures = build_customer_additional_figures("all")

    assert len(figures) == 7

    for number, figure in enumerate(figures, start=14):
        assert len(figure.data) > 0
        assert len(figure.to_json()) > 300
        print(
            f"CHART {number}: PASS | "
            f"type={figure.data[0].type} | "
            f"traces={len(figure.data)}",
            flush=True
        )

    print("CHECK 3: SEGMENT FILTER", flush=True)
    filtered = build_customer_additional_figures("Repeat Champions")

    assert len(filtered) == 7
    assert sum(filtered[3].data[0].y) == 1310

    print("SEGMENT FILTER: PASS")
    print("SEVEN-CHART DIAGNOSTIC: PASS")

except Exception:
    traceback.print_exc()
    sys.exit(1)
