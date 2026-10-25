# Project APEX — Phase 6 Delivery Risk Model Card

## Purpose

Historical classification and risk ranking of orders delivered after their promised calendar date.

## Data

Source: Olist Brazilian e-commerce dataset, processed through the Project APEX PostgreSQL and dbt warehouse.

Observation grain: One order.

Eligible delivery records: 96,470.
Historically late orders: 6,534.
Late rate: 6.7731%.

## Chronological Design

Training: January 2017 through April 2018.
Validation: May through June 2018.
Held-out test: July through August 2018.

Sparse 2016 boundary records excluded from modeling.

Test records: 12,507.
Test late orders: 601.

## Candidate Models

Historical prevalence baseline.
Strict logistic regression.
Strict histogram gradient boosting.
Expanded logistic regression.
Expanded histogram gradient boosting.

Model selection used validation average precision.

## Selected Candidate

Expanded logistic regression.

Validation average precision: 0.105983.
Validation ROC-AUC: 0.744223.
Validation Brier score: 0.038197.

Locked classification threshold: 0.0785046.
Threshold optimized for F2 using validation records only.

## Final Held-Out Performance

Average precision: 0.079666.
ROC-AUC: 0.619684.
Brier score: 0.050393.
Precision: 0.066982.
Recall: 0.730449.
F2: 0.245032.

True negatives: 5,791.
False positives: 6,115.
False negatives: 162.
True positives: 439.

The test prevalence baseline average precision is 0.048053.
The historical prevalence baseline Brier score is 0.046550.

The candidate has better average precision than the prevalence baseline but worse Brier score.

## Operational Ranking Evidence

Top 1 percent: 126 orders reviewed, 28 late orders detected.
Top 5 percent: 626 orders reviewed, 73 late orders detected.
Top 10 percent: 1,251 orders reviewed, 101 late orders detected.
Top 20 percent: 2,502 orders reviewed, 153 late orders detected.
Top 50 percent: 6,254 orders reviewed, 428 late orders detected.

These are historical identification counts, not prevented failures.

## Prediction Availability

The expanded feature group contains promised delivery duration, item value, freight and item count.

Point-in-time availability of these fields at the proposed prediction event has not been independently established.

The expanded model is therefore a research candidate, not a certified checkout-time production model.

## Calibration

Observed test late rates are lower than average predicted probabilities in both July and August 2018.

The model's raw probabilities are not approved for direct financial expected-value calculations.

## Intended Uses

Historical risk ranking.
Model evaluation demonstrations.
Retrospective capacity analysis.
Transparent business scenario exploration with stated assumptions.

## Prohibited Interpretations

Do not claim deployment readiness.
Do not claim prevented late deliveries.
Do not claim causal effects.
Do not present model probabilities as verified individual failure probabilities.
Do not present hypothetical savings as realized financial results.

## Reproduction

Rebuild the Phase 3 and Phase 4 warehouse.
Execute the Phase 6 feasibility, feature and validation SQL scripts.
Run the training script to reproduce validation-based selection.
Compare the locked model and test diagnostics against recorded evidence.

The final test must not be reused repeatedly to tune model hyperparameters or thresholds.

## Security

Only load locally generated, trusted joblib model artifacts.
Do not commit database credentials or environment secrets.
