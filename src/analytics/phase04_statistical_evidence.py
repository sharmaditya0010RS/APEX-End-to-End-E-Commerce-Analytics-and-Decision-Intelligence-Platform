from pathlib import Path
import json
import os

import numpy as np
import pandas as pd
import psycopg
from scipy import stats
from dotenv import load_dotenv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "statistics"
OUT.mkdir(parents=True, exist_ok=True)
load_dotenv(ROOT / ".env")

with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"]
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT is_late_calendar, average_review_score
            FROM analytics.v_order_intelligence
            WHERE delivery_sla_eligible = TRUE
              AND average_review_score IS NOT NULL
        """)
        rows = cursor.fetchall()

data = pd.DataFrame(rows, columns=["late", "review_score"])
data["review_score"] = pd.to_numeric(data["review_score"])

late = data.loc[data["late"] == True, "review_score"].to_numpy()
ontime = data.loc[data["late"] == False, "review_score"].to_numpy()

if len(late) < 2 or len(ontime) < 2:
    raise RuntimeError("Insufficient data for statistical comparison")

mean_late = float(late.mean())
mean_ontime = float(ontime.mean())
difference = mean_late - mean_ontime

standard_error = np.sqrt(
    late.var(ddof=1) / len(late)
    + ontime.var(ddof=1) / len(ontime)
)

test = stats.ttest_ind(late, ontime, equal_var=False)

pooled_sd = np.sqrt(
    ((len(late) - 1) * late.var(ddof=1)
    + (len(ontime) - 1) * ontime.var(ddof=1))
    / (len(late) + len(ontime) - 2)
)

effect_size = difference / pooled_sd if pooled_sd > 0 else None

result = {
    "late_reviewed_orders": len(late),
    "on_time_reviewed_orders": len(ontime),
    "mean_review_late": mean_late,
    "mean_review_on_time": mean_ontime,
    "mean_difference_late_minus_on_time": difference,
    "welch_t_statistic": float(test.statistic),
    "p_value": float(test.pvalue),
    "cohens_d": float(effect_size) if effect_size is not None else None,
    "approx_95pct_ci_lower": float(difference - 1.96 * standard_error),
    "approx_95pct_ci_upper": float(difference + 1.96 * standard_error),
    "analysis_type": "Observational association",
    "causal_claim": False
}

(OUT / "delivery_review_statistical_result.json").write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

plt.figure(figsize=(10, 6))
plt.bar(
    ["On-time", "Late"],
    [mean_ontime, mean_late],
    yerr=[
        1.96 * ontime.std(ddof=1) / np.sqrt(len(ontime)),
        1.96 * late.std(ddof=1) / np.sqrt(len(late))
    ],
    capsize=6
)
plt.ylabel("Average Review Score")
plt.title("Review Score by Delivery Performance: Approximate 95% CIs")
plt.tight_layout()
plt.savefig(OUT / "delivery_review_confidence_intervals.png", dpi=200)
plt.close()

print(json.dumps(result, indent=2))
print("STATISTICAL ANALYSIS COMPLETED")
