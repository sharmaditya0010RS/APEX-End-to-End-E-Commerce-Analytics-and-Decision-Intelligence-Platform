# Project APEX — Phase 2 Data Quality Decisions

## Investigation Scope
Nine original Olist source tables were profiled.
Source records were not altered.
Thirteen exploratory visual reports were generated.

## Confirmed Findings
Total source rows: 1,550,922
Total source columns: 52
Missing cells: 153,259
Exact duplicate rows: 261,831
Duplicates in geolocation: 261,831
Orphans in six tested relationships: 0
Orders without payment records: 1
Orders without review records: 768
Products without category: 610
Products with unmapped non-null category: 13

## DQ-001 Geographic Relationships
Retain the entire original geolocation source.
Create a deterministic, unique postal-prefix geographic lookup.
Use median coordinates as an initial candidate rule.
Validate outliers and spatial dispersion before certification.
Prevent many-to-many fanout into customer and seller analysis.

## DQ-002 Review Text
Preserve missing optional review titles and messages.
Do not fabricate text or exclude valid review scores.

## DQ-003 Delivery Lifecycle
Use order status to interpret missing delivery dates.
Only eligible delivered orders enter historical on-time calculations.
Investigate delivered orders with missing delivery timestamps.

## DQ-004 Product Categories
Preserve original category identifiers.
Create an Unknown reporting category for missing classifications.
Flag untranslated categories independently.

## DQ-005 Payment Coverage
Keep orders without payments in the order-level fact.
Track payment coverage separately.
Never use an inner payment join that silently drops orders.

## DQ-006 Review Coverage
Keep orders without review records.
Do not infer satisfaction scores for missing reviews.

## DQ-007 Transaction Grain
Preserve distinct order item and payment sequence records.
Avoid flattening multi-item and multi-payment relationships without preaggregation.

## DQ-008 Reconciliation
Verify source-to-raw row counts.
Test unique dimension keys.
Detect unexpected increases in fact rows after joins.

## DQ-009 Source Lineage
Maintain source hashes and ingestion audit records.
Keep raw source files unchanged.

## DQ-010 On-Time Delivery Definition
Compare timestamp-level and calendar-date-level lateness.
Select a documented primary SLA definition.
Retain the alternative definition for sensitivity analysis.

## Data Limitations
Historical data is not live company reporting.
Profit and marketing spend cannot be established from these tables.
Predictions require point-in-time controls.
Scenarios are estimates, not realized outcomes.

## Status
Data profiling verified.
Warehouse transformations not yet implemented.
