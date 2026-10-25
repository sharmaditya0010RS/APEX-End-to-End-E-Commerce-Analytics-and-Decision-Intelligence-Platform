from pathlib import Path
import json
import os

import joblib
import numpy as np
import pandas as pd
import psycopg

from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_curve,
    roc_auc_score
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports" / "modeling"
MODEL_DIR = ROOT / "models"

OUT.mkdir(parents=True, exist_ok=True)
MODEL_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")

QUERY = """
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
WHERE order_purchase_timestamp >= DATE '2017-01-01'
  AND order_purchase_timestamp < DATE '2018-07-01'
ORDER BY order_purchase_timestamp, order_id
"""

with psycopg.connect(
    host="127.0.0.1",
    port=5433,
    dbname=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    options="-c max_parallel_workers_per_gather=0 -c work_mem=16MB"
) as conn:
    with conn.cursor() as cursor:
        cursor.execute(QUERY)
        rows = cursor.fetchall()
        columns = [column.name for column in cursor.description]

data = pd.DataFrame(rows, columns=columns)
data["order_purchase_timestamp"] = pd.to_datetime(data["order_purchase_timestamp"])

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
    data[column] = pd.to_numeric(data[column], errors="raise")

train = data.loc[
    data["order_purchase_timestamp"] < pd.Timestamp("2018-05-01")
].copy()

validation = data.loc[
    data["order_purchase_timestamp"] >= pd.Timestamp("2018-05-01")
].copy()

assert len(train) == 70851
assert len(validation) == 12845
assert int(train["target_late"].sum()) == 5416
assert int(validation["target_late"].sum()) == 514
assert train["order_id"].is_unique
assert validation["order_id"].is_unique
assert not set(train["order_id"]).intersection(set(validation["order_id"]))

STRICT = [
    "customer_state",
    "purchase_month_number",
    "purchase_day_of_week",
    "purchase_hour"
]

EXPANDED = STRICT + [
    "promised_delivery_days",
    "gross_item_value",
    "freight_value",
    "item_count"
]

TARGET = "target_late"
CATEGORICAL = ["customer_state"]

def make_pipeline(features, estimator):
    numeric = [feature for feature in features if feature not in CATEGORICAL]

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(
                        handle_unknown="ignore",
                        sparse_output=False
                    ))
                ]),
                CATEGORICAL
            ),
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler())
                ]),
                numeric
            )
        ],
        remainder="drop"
    )

    return Pipeline([
        ("preprocessing", preprocessing),
        ("estimator", estimator)
    ])

def logistic():
    return LogisticRegression(
        max_iter=1500,
        solver="lbfgs",
        random_state=42
    )

def boosting():
    return HistGradientBoostingClassifier(
        max_iter=160,
        learning_rate=0.06,
        max_leaf_nodes=15,
        min_samples_leaf=60,
        l2_regularization=10.0,
        random_state=42
    )

experiments = [
    (
        "historical_prevalence",
        "none",
        None,
        DummyClassifier(strategy="prior")
    ),
    (
        "strict_logistic",
        "strict",
        STRICT,
        make_pipeline(STRICT, logistic())
    ),
    (
        "strict_gradient_boosting",
        "strict",
        STRICT,
        make_pipeline(STRICT, boosting())
    ),
    (
        "expanded_logistic",
        "expanded",
        EXPANDED,
        make_pipeline(EXPANDED, logistic())
    ),
    (
        "expanded_gradient_boosting",
        "expanded",
        EXPANDED,
        make_pipeline(EXPANDED, boosting())
    )
]

results = []
trained = {}

y_train = train[TARGET].astype(int)
y_validation = validation[TARGET].astype(int)

for name, feature_group, features, model in experiments:
    if features is None:
        x_train = np.zeros((len(train), 1))
        x_validation = np.zeros((len(validation), 1))
    else:
        x_train = train[features]
        x_validation = validation[features]

    model.fit(x_train, y_train)

    probabilities = model.predict_proba(x_validation)[:, 1]

    if not np.isfinite(probabilities).all():
        raise RuntimeError(f"Invalid predictions for {name}")

    if ((probabilities < 0) | (probabilities > 1)).any():
        raise RuntimeError(f"Out-of-range probabilities for {name}")

    metrics = {
        "model": name,
        "feature_group": feature_group,
        "train_rows": len(train),
        "validation_rows": len(validation),
        "train_late_rate": float(y_train.mean()),
        "validation_late_rate": float(y_validation.mean()),
        "validation_average_precision": float(
            average_precision_score(y_validation, probabilities)
        ),
        "validation_roc_auc": float(
            roc_auc_score(y_validation, probabilities)
        ),
        "validation_brier_score": float(
            brier_score_loss(y_validation, probabilities)
        )
    }

    results.append(metrics)
    trained[name] = {
        "model": model,
        "features": features,
        "probabilities": probabilities
    }

    print(
        f"{name}: "
        f"AP={metrics['validation_average_precision']:.5f}, "
        f"ROC_AUC={metrics['validation_roc_auc']:.5f}, "
        f"Brier={metrics['validation_brier_score']:.5f}",
        flush=True
    )

results = sorted(
    results,
    key=lambda row: (
        -row["validation_average_precision"],
        row["validation_brier_score"]
    )
)

winner = results[0]
selected = trained[winner["model"]]

precision, recall, thresholds = precision_recall_curve(
    y_validation,
    selected["probabilities"]
)

beta_squared = 4.0

f2 = (
    (1 + beta_squared) * precision[:-1] * recall[:-1]
    / np.maximum(
        beta_squared * precision[:-1] + recall[:-1],
        1e-12
    )
)

best_index = int(np.argmax(f2))
selected_threshold = float(thresholds[best_index])

validation_predictions = validation[
    ["order_id", "order_purchase_timestamp", TARGET]
].copy()

validation_predictions["predicted_late_probability"] = selected["probabilities"]
validation_predictions["predicted_late_at_selected_threshold"] = (
    selected["probabilities"] >= selected_threshold
).astype(int)

validation_predictions.to_csv(
    OUT / "phase06_validation_predictions.csv",
    index=False
)

pd.DataFrame(results).to_csv(
    OUT / "phase06_validation_leaderboard.csv",
    index=False
)

metadata = {
    "prediction_task": "calendar_date_late_delivery",
    "unit_of_analysis": "order",
    "prediction_scenario": "order_placement_candidate",
    "training_period": "2017-01 through 2018-04",
    "validation_period": "2018-05 through 2018-06",
    "final_test_period": "2018-07 through 2018-08",
    "test_evaluated": False,
    "selection_metric": "validation_average_precision",
    "selected_model": winner["model"],
    "selected_feature_group": winner["feature_group"],
    "selected_features": selected["features"],
    "selected_threshold": selected_threshold,
    "threshold_selection": "maximum_validation_F2",
    "validation_F2": float(f2[best_index]),
    "validation_results": results,
    "expanded_features_point_in_time_verified": False,
    "causal_claim": False
}

joblib.dump(
    selected["model"],
    MODEL_DIR / "phase06_selected_delivery_risk.joblib"
)

(OUT / "phase06_model_selection.json").write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8"
)

print(json.dumps({
    "selected_model": winner["model"],
    "selected_feature_group": winner["feature_group"],
    "validation_average_precision": winner["validation_average_precision"],
    "validation_roc_auc": winner["validation_roc_auc"],
    "validation_brier_score": winner["validation_brier_score"],
    "selected_threshold": selected_threshold,
    "validation_F2": float(f2[best_index]),
    "final_test_evaluated": False
}, indent=2))

print("PHASE 6 TRAINING AND VALIDATION COMPLETED")
