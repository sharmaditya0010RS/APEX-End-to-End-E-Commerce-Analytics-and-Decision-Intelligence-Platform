from pathlib import Path
import json
import math

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs" / "modeling" / "evidence"

def predictive_evidence():
    def read_json(name):
        return json.loads(
            (EVIDENCE / name).read_text(encoding="utf-8-sig")
        )

    def read_csv(name):
        return pd.read_csv(EVIDENCE / name)

    selection = read_json("phase06_model_selection.json")
    test = read_json("phase06_final_test_results.json")
    operational = read_json("phase06_operational_diagnostics.json")
    leaderboard = read_csv("phase06_validation_leaderboard.csv")
    budgets = read_csv("phase06_operational_review_budgets.csv")
    calibration = read_csv("phase06_test_calibration_summary.csv")
    monthly = read_csv("phase06_test_monthly_drift.csv")

    if len(leaderboard) != 5:
        raise ValueError("Five validation experiments required")

    if len(budgets) != 6:
        raise ValueError("Six capacity levels required")

    if len(monthly) != 2:
        raise ValueError("Two test months required")

    if not 1 <= len(calibration) <= 10:
        raise ValueError("Invalid calibration bins")

    if int(test["test_rows"]) != 12507:
        raise ValueError("Test order count mismatch")

    if int(test["test_late_orders"]) != 601:
        raise ValueError("Test late-order count mismatch")

    if selection["selected_model"] != test["model"]:
        raise ValueError("Selected and evaluated models differ")

    if not math.isclose(
        float(selection["selected_threshold"]),
        float(test["locked_threshold"]),
        abs_tol=1e-12
    ):
        raise ValueError("Locked threshold mismatch")

    if int(budgets.iloc[-1]["actual_late_detected"]) != 601:
        raise ValueError("Review capacity evidence mismatch")

    if int(calibration["observations"].sum()) != 12507:
        raise ValueError("Calibration counts mismatch")

    if int(monthly["orders"].sum()) != 12507:
        raise ValueError("Monthly test counts mismatch")

    if int(test["true_positive"]) + int(test["false_negative"]) != 601:
        raise ValueError("Confusion matrix positive-class mismatch")

    if (
        int(test["true_negative"]) + int(test["false_positive"])
    ) != 11906:
        raise ValueError("Confusion matrix negative-class mismatch")

    required_metrics = [
        "validation_average_precision",
        "validation_roc_auc",
        "validation_brier_score"
    ]

    for metric in required_metrics:
        if not leaderboard[metric].map(math.isfinite).all():
            raise ValueError(f"Invalid metric: {metric}")

    return {
        "selection": selection,
        "test": test,
        "operational": operational,
        "leaderboard": leaderboard,
        "budgets": budgets,
        "calibration": calibration,
        "monthly": monthly
    }
