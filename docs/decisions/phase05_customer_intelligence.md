# Project APEX — Phase 5 Customer Intelligence

## Scope

Historical customer RFM, descriptive customer segmentation and monthly repeat-purchase cohort analysis using delivered-status Olist marketplace orders.

## Verified baseline

Delivered orders: 96,478
Customers with delivered orders: 93,358
Repeat customers: 2,801
Observed repeat-customer percentage: 3.000%
Delivered gross item value: BRL 13,221,498.11

## RFM definitions

Recency: days from each customer's last delivered-order purchase date to one day after the final delivered-order purchase date in the extract.

Frequency: distinct delivered orders observed for that customer.

Monetary value: sum of recorded item prices for the customer's delivered orders, excluding freight.

RFM is descriptive, not a churn prediction or true lifetime-value estimate.

## Segmentation

Six mutually exclusive customer groups are defined using delivered-order frequency and observed median recency and monetary value.

The segment names describe patterns within the source dataset; they are not externally validated behavioral classes.

## Cohort methodology

Cohorts are based on the month of a customer's first observed delivered-order purchase.

The cohort matrix covers month offsets 0 through 12.

Monthly activity is the percentage of original cohort customers with at least one delivered-order purchase in the corresponding month.

Zero means no activity during a fully observable calendar month.

NULL means the full month is outside the supported observation window.

This is monthly purchasing activity rather than subscription retention or a survival estimate.

## Observation boundary

Latest purchase among all statuses: 2018-10-17.
Latest delivered-order purchase: 2018-08-29.
Conservative analysis cutoff: 2018-08-29.
Last eligible complete delivered-order calendar month: July 2018.

Sparse September and October purchases must not extend the delivered-order observation window.

Calendar completeness is an analytical assumption, not independent proof of exhaustive source coverage.

## Cohort evidence

Distinct acquisition cohorts: 23.
Cohort matrix cells: 299.
Fully observable cells: 208.
Observed zero-activity cells: 33.
Unobservable cells: 91.

## Validation

RFM integrity and reconciliation: six checks.
Customer segmentation and cohort activity: eight checks.
Completed cohort matrix: seven checks.
Delivered-order cutoff integrity: three checks.

All passed in the reviewed Phase 5 execution logs before the final RFM reference-date refinement.

The final RFM refinement must pass downstream regression checks before Phase 5 sign-off.

## Business interpretation

Observed repeat purchasing is limited within the available historical dataset.

High-Value One-Time customers dominate observed delivered gross item value, but the segment's name is relative to the source population median.

The data cannot establish actual future churn, lifetime value, causal retention drivers or realized financial uplift.

## Future dashboard dependencies

Customer segmentation, repeat purchasing, cohort activity, eligible denominators, and masked unobservable periods will feed the five-page Plotly Dash application and the final Power BI report.

## Reproduction

Execute the Phase 5 SQL view scripts in dependency order after building the Phase 3 and Phase 4 warehouse.

Use session-local max_parallel_workers_per_gather=0 for complex analytical verification on the existing 64 MB Docker shared-memory configuration.
