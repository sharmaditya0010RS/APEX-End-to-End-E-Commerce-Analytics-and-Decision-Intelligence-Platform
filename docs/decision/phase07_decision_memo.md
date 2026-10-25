# Project APEX — Phase 7 Decision Intelligence Memo

## Executive Decision

NO-GO for production deployment under the illustrative base-case economics.

A limited prospective pilot may be considered after validating feature availability, intervention costs, causal effectiveness and operational feasibility.

No realized savings or prevented deliveries are claimed.

## Observed Historical Evidence

The final held-out evaluation covers 12,507 orders and 601 historically late deliveries.

The selected research model is expanded logistic regression.

Test average precision: 0.079666.
Test ROC-AUC: 0.619684.
Test Brier score: 0.050393.

The model is not deployment-approved and its probabilities are poorly calibrated.

## Review-Capacity Evidence

At 1% capacity: 126 orders reviewed, 28 historically late orders identified.

At 5% capacity: 626 orders reviewed, 73 historically late orders identified.

At 10% capacity: 1,251 orders reviewed, 101 historically late orders identified.

At 20% capacity: 2,502 orders reviewed, 153 historically late orders identified.

These are observed historical identification counts, not successfully prevented delivery failures.

## Explicitly Hypothetical Assumptions

Intervention effectiveness: 10%, 25% or 50%.

Review cost per order: BRL 2, BRL 5 or BRL 10.

Financial value per prevented late delivery: BRL 20, BRL 50 or BRL 100.

The resulting sensitivity grid contains 162 scenarios.

These monetary and effectiveness assumptions are not measured from Olist data.

## Base-Case Scenario

Assumed effectiveness: 25%.
Assumed review cost: BRL 5 per order.
Assumed prevention value: BRL 50.

Capacity 1%: hypothetical net BRL -280.00.
Capacity 5%: hypothetical net BRL -2,217.50.
Capacity 10%: hypothetical net BRL -4,992.50.
Capacity 20%: hypothetical net BRL -10,597.50.

No evaluated capacity is financially viable under this illustrative base case.

## Break-Even Requirements

At 25% assumed effectiveness and BRL 5 review cost:

Capacity 1%: BRL 90.00 per successful prevention.
Capacity 5%: approximately BRL 171.51.
Capacity 10%: approximately BRL 247.72.
Capacity 20%: approximately BRL 327.06.
Capacity 50%: approximately BRL 292.24.
Capacity 100%: approximately BRL 416.21.

## Model Versus Random Review

Random-review outcomes are mathematical expectations based on the held-out population prevalence, not experimentally observed operational results.

The incremental model-versus-random calculation assumes identical per-order review costs and intervention effectiveness for both strategies.

A positive model-versus-random difference does not imply positive net value or an actionable intervention.

## Recommendation

Do not deploy the existing candidate or advertise projected savings as realized benefits.

Before a pilot:

1. Validate the timestamp-level availability of all proposed predictors.
2. Establish actual logistics intervention options and unit costs.
3. Define operational review capacity and a prospective intervention policy.
4. Evaluate discrimination, calibration and operational stability on future data.
5. Design a controlled study that can estimate causal intervention effectiveness.
6. Establish decision thresholds using prospective evidence and agreed business costs.

## Automation and Reproducibility

The scenario engine and independent validators are reproducible local scripts.

No scheduled operational automation or automated intervention system has been deployed.

## Portfolio Interpretation

This phase demonstrates sensitivity modeling, break-even analysis, constrained operational prioritization, financial assumption transparency and decision governance.

The outcome is a conditional no-go under the base case, not an unsuccessful analysis.
