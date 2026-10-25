# BUSINESS REQUIREMENTS DOCUMENT

## 1. Executive Context
An analytics consulting team has been engaged in a simulated business scenario to investigate marketplace performance using historical Olist data.

## 2. Stakeholder Decisions
Executive leadership: Prioritize commercial and operational initiatives.
Commercial management: Identify revenue and category concentration.
Customer management: Understand repeat purchasing and satisfaction.
Operations management: Prioritize delivery improvement opportunities.
Seller management: Identify sellers requiring intervention.
Analytics engineering: Maintain trusted reporting datasets.

## 3. Functional Requirements
FR-001: Display consolidated order, revenue and delivery KPIs.
FR-002: Analyze revenue over time and across categories.
FR-003: Segment customers using reproducible behavioral definitions.
FR-004: Analyze customer purchase cohorts and follow-up behavior.
FR-005: Investigate estimated versus actual delivery dates.
FR-006: Rank sellers by volume and service reliability.
FR-007: Evaluate product and category performance.
FR-008: Compare marketplace performance geographically.
FR-009: Present validated forecasts and predictive risk estimates.
FR-010: Calculate assumption-driven intervention scenarios.
FR-011: Support cross-filtering and relevant drillthrough.
FR-012: Expose metric definitions, data coverage and limitations.

## 4. Non-Functional Requirements
NFR-001: Business KPIs must be reproducible from warehouse queries.
NFR-002: Source loading must not silently duplicate records.
NFR-003: Critical transformations must have automated tests.
NFR-004: Database credentials must not enter source control.
NFR-005: Reports must be accessible and understandable to non-technical stakeholders.
NFR-006: Report performance must be benchmarked under documented conditions.
NFR-007: Source provenance and data refresh dates must be visible.
NFR-008: All financial recommendations must distinguish assumptions from observed outcomes.
NFR-009: Predictive training and evaluation must prevent data leakage.
NFR-010: Documented deployment and recovery procedures must exist.

## 5. Constraints
The dataset covers historical periods and is not a current operational feed.
True profit and customer acquisition cost cannot be computed from available source columns alone.
Observed correlations do not establish intervention causality.
Public portfolio use must respect dataset license conditions.

## 6. Requirements Approval
All stakeholders are simulated.
This document is a portfolio specification and not an actual Olist-approved business requirement.
