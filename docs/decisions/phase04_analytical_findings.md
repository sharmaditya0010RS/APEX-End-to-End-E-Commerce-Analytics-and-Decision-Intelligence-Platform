# Project APEX — Phase 4 Analytical Findings

## Executive Summary

This analysis uses historical Brazilian e-commerce transactions from the original Olist dataset.

The analytical warehouse contains 99,441 orders associated with 96,096 distinct customer identities.

Total observed gross item value is BRL 13,591,643.70, excluding freight.

## Finding F04-001 — Delivery Reliability

Delivered orders: 96,478
Orders eligible for calendar-date SLA assessment: 96,470
Orders delivered after the promised calendar date: 6,534
Calendar-date late delivery rate: 6.7731%
Calendar-date on-time rate: 93.2269%

Eight delivered orders have insufficient timestamp coverage for SLA classification.

The calendar-date SLA is a documented analytical assumption based on an end-of-day delivery promise.

## Finding F04-002 — Delivery Performance and Satisfaction

Orders with eligible delivery dates and review scores:
Late: 6,381
On time: 89,443

Mean review score:
Late: 2.2718
On time: 4.2906

Difference, late minus on time: -2.0188 points
Approximate 95% confidence interval: [-2.0580, -1.9795]
Cohen's d: -1.7096
Welch t-test: p < 0.001

Interpretation:
Late-delivered orders have substantially lower observed review scores in this historical sample.

This is an observational association, not a causal estimate.
Product quality, seller characteristics, geographic region, order value, review selection, and other factors may contribute to the difference.

## Finding F04-003 — Commercial Measurement

Gross item value: BRL 13,591,643.70

This represents recorded item prices, excluding freight.
It is not verified company net revenue, recognized accounting revenue, profit, or payment receipts.

Monthly visualizations include historical boundary periods that may be incomplete.

## Finding F04-004 — Seller Attribution

Seller-order analytical records: 100,010

A marketplace order involving multiple sellers can contribute one seller-order observation to each seller.

Seller-order counts must not be summed to estimate distinct marketplace orders.

Seller-attributed item value is allocated from actual item records.

Seller late-delivery rates are displayed only when at least 30 eligible seller-order observations exist.

A missing or statistically ineligible rate must not be interpreted as zero.

## Visual Evidence

13 source profiling and quality graphics.
20 Phase 4 business analysis graphics.
1 confidence-interval graphic.

The collection includes commercial, customer, seller, delivery, geographic, and data-quality views.

## Visual Interpretation Limitations

Distributions capped with clip() place observations beyond the cap at the boundary.
These charts are exploratory and must not be presented as truncated distributions without an explicit boundary annotation.

Charts showing all historical months may include incomplete opening or closing months.
Seller and geographic comparisons may require confidence intervals and sample-size controls.

## Reconciliation Evidence

Five Phase 4 SQL validation checks passed.
Order-level analytical view: 99,441 records.
Calendar-date late orders: 6,534.
SLA-eligible orders: 96,470.
Seller-attributed item value reconciles to order-item prices.

The Phase 3 warehouse previously passed 20 dbt tests.

## Future Investigations

Analyze purchasing cohorts with consistent observation windows.
Investigate geographic delivery differences with appropriate denominators.
Compare sellers using volume and uncertainty thresholds.
Estimate adjusted associations between delivery lateness and customer satisfaction.
Evaluate potential interventions through explicit assumptions rather than invented realized savings.
