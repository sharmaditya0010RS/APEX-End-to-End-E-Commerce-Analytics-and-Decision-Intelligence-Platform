from pathlib import Path
import hashlib
import json
import os

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psycopg

from dotenv import load_dotenv
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    brier_score_loss,
    precision_score,
    recall_score,
    f1_score,
    fbeta_score,
    confusion_matrix,
    precision_recall_curve,
    roc_curve
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "modeling"
FIGURES = OUT / "figures"
MODEL_PATH = ROOT / "models" / "phase06_selected_delivery_risk.joblib"
META_PATH = OUT / "phase06_model_selection.json"
RESULT_PATH = OUT / "phase06_final_test_results.json"
PREDICTION_PATH = OUT / "phase06_final_test_predictions.csv"

if RESULT_PATH.exists() or PREDICTION_PATH.exists():
    raise RuntimeError("Final test evidence already exists. Refusing to overwrite it.")

FIGURES.mkdir(parents=True, exist_ok=True)
load_dotenv(ROOT / ".env")

metadata = json.loads(META_PATH.read_text(encoding="utf-8"))

if metadata["test_evaluated"] is not False:
    raise RuntimeError("Model selection metadata indicates prior test evaluation.")

if metadata["selected_model"] != "expanded_logistic":
    raise RuntimeError("Unexpected model identity; do not evaluate.")

features = metadata["selected_features"]
threshold = float(metadata["selected_threshold"])

if not features or not 0 < threshold < 1:
    raise RuntimeError("Invalid locked model selection metadata.")

model_hash = hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest()
model = joblib.load(MODEL_PATH)

query = """
SELECT
    order_id,
    order_purchase_timestamp,
    customer_state,
    purchase_month_number,
    purchase_day_of_week,
    purchase_hour,
    promised_delivery_days,
    gross_item_value,
    freight_value,
    item_count,
    target_late
FROM analytics.v_delivery_risk_features
WHERE order_purchase_timestamp >= DATE '2018-07-01'
  AND order_purchase_timestamp < DATE '2018-09-01'
ORDER BY order_purchase_timestamp, order_id
"""

with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    options="-c max_parallel_workers_per_gather=0 -c work_mem=16MB"
) as connection:
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [item.name for item in cursor.description]
        rows = cursor.fetchall()

test = pd.DataFrame(rows, columns=columns)

for column in [
    "purchase_month_number",
    "purchase_day_of_week",
    "purchase_hour",
    "promised_delivery_days",
    "gross_item_value",
    "freight_value",
    "item_count",
    "target_late"
]:
    test[column] = pd.to_numeric(test[column], errors="raise")

test["order_purchase_timestamp"] = pd.to_datetime(
    test["order_purchase_timestamp"]
)

if len(test) != 12507:
    raise RuntimeError("Test sample size does not reconcile.")

if int(test["target_late"].sum()) != 601:
    raise RuntimeError("Test late-order count does not reconcile.")

if not test["order_id"].is_unique:
    raise RuntimeError("Duplicate order IDs detected.")

if test[features].isna().any().any():
    raise RuntimeError("Unexpected missing test features.")

y = test["target_late"].astype(int).to_numpy()
probabilities = model.predict_proba(test[features])[:, 1]

if not np.isfinite(probabilities).all():
    raise RuntimeError("Nonfinite predictions.")

if np.any((probabilities < 0) | (probabilities > 1)):
    raise RuntimeError("Probabilities outside [0,1].")

predictions = (probabilities >= threshold).astype(int)
tn, fp, fn, tp = confusion_matrix(y, predictions, labels=[0, 1]).ravel()

results = {
    "model": metadata["selected_model"],
    "feature_group": metadata["selected_feature_group"],
    "test_period": "2018-07-01 to 2018-08-31",
    "test_rows": int(len(test)),
    "test_late_orders": int(y.sum()),
    "test_late_rate": float(y.mean()),
    "model_sha256": model_hash,
    "locked_threshold": threshold,
    "test_average_precision": float(average_precision_score(y, probabilities)),
    "test_roc_auc": float(roc_auc_score(y, probabilities)),
    "test_brier_score": float(brier_score_loss(y, probabilities)),
    "test_precision": float(precision_score(y, predictions, zero_division=0)),
    "test_recall": float(recall_score(y, predictions, zero_division=0)),
    "test_f1": float(f1_score(y, predictions, zero_division=0)),
    "test_f2": float(fbeta_score(y, predictions, beta=2, zero_division=0)),
    "true_negative": int(tn),
    "false_positive": int(fp),
    "false_negative": int(fn),
    "true_positive": int(tp),
    "test_prevalence_baseline_ap": float(y.mean()),
    "test_historical_prevalence_brier": float(
        brier_score_loss(
            y,
            np.full(len(y), metadata["validation_results"][
                next(
                    i for i, entry in enumerate(metadata["validation_results"])
                    if entry["model"] == "historical_prevalence"
                )
            ]["train_late_rate"])
        )
    ),
    "expanded_features_point_in_time_verified": False,
    "test_used_for_model_selection": False
}

evidence = test[
    ["order_id", "order_purchase_timestamp", "target_late"]
].copy()
evidence["predicted_late_probability"] = probabilities
evidence["predicted_late_class"] = predictions

precision, recall, _ = precision_recall_curve(y, probabilities)
fpr, tpr, _ = roc_curve(y, probabilities)

plt.figure(figsize=(9, 6))
plt.plot(recall, precision, label="Selected model")
plt.axhline(y.mean(), linestyle="--", label="Test prevalence")
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title("Held-Out Test Precision-Recall Curve")
plt.legend()
plt.tight_layout()
plt.savefig(FIGURES / "phase06_test_precision_recall.png", dpi=180)
plt.close()

plt.figure(figsize=(9, 6))
plt.plot(fpr, tpr, label="Selected model")
plt.plot([0, 1], [0, 1], linestyle="--", label="Random ranking")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("Held-Out Test ROC Curve")
plt.legend()
plt.tight_layout()
plt.savefig(FIGURES / "phase06_test_roc.png", dpi=180)
plt.close()

plt.figure(figsize=(8, 6))
matrix = np.array([[tn, fp], [fn, tp]])
plt.imshow(matrix, cmap="Blues")
plt.xticks([0, 1], ["Predicted on time", "Predicted late"])
plt.yticks([0, 1], ["Actually on time", "Actually late"])
for row in range(2):
    for column in range(2):
        plt.text(
            column,
            row,
            f"{matrix[row, column]:,}",
            ha="center",
            va="center"
        )
plt.title("Held-Out Test Confusion Matrix")
plt.tight_layout()
plt.savefig(FIGURES / "phase06_test_confusion_matrix.png", dpi=180)
plt.close()

calibration = pd.DataFrame({
    "probability": probabilities,
    "actual": y
})

calibration["bucket"] = pd.qcut(
    calibration["probability"],
    q=10,
    duplicates="drop"
)

calibration_summary = (
    calibration.groupby("bucket", observed=True)
    .agg(
        predicted_probability=("probability", "mean"),
        observed_late_rate=("actual", "mean"),
        observations=("actual", "size")
    )
    .reset_index(drop=True)
)

plt.figure(figsize=(8, 6))
plt.plot([0, 1], [0, 1], linestyle="--", label="Perfect calibration")
plt.plot(
    calibration_summary["predicted_probability"],
    calibration_summary["observed_late_rate"],
    marker="o",
    label="Selected model"
)
plt.xlabel("Mean Predicted Late Probability")
plt.ylabel("Observed Late Rate")
plt.title("Held-Out Test Reliability Diagram")
plt.legend()
plt.tight_layout()
plt.savefig(FIGURES / "phase06_test_calibration.png", dpi=180)
plt.close()

evidence.to_csv(PREDICTION_PATH, index=False)
calibration_summary.to_csv(
    OUT / "phase06_test_calibration_summary.csv",
    index=False
)

RESULT_PATH.write_text(
    json.dumps(results, indent=2),
    encoding="utf-8"
)

print(json.dumps(results, indent=2))
print("HELD-OUT TEST EVALUATION COMPLETED")
