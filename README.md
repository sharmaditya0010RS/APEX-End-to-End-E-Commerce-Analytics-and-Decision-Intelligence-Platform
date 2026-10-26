# APEX | E-Commerce Analytics & Decision Intelligence Platform

**Turning historical e-commerce data into measurable insights, predictive evidence, and business decisions.**

**PostgreSQL • SQL • dbt • Python • Machine Learning • Plotly Dash • Docker**

---

## Overview

APEX is an end-to-end **Analytics Engineering, Business Intelligence, and Decision Intelligence** platform built using the Brazilian Olist e-commerce dataset.

The project transforms raw transactional data into a structured analytics warehouse, evaluates customer behavior and delivery reliability, assesses predictive model performance and explores the financial feasibility of hypothetical business interventions.

It combines **data engineering, statistical analysis, customer intelligence, machine learning, interactive dashboards and decision-support analytics** in a single portfolio project.

## Project at a Glance

| Business Metric | Historical Result |
|---|---:|
| Orders Analyzed | **99,441** |
| Unique Customer Identities | **96,096** |
| Gross Merchandise Value | **R$13.59M** |
| SLA-Eligible Orders | **96,470** |
| Late Deliveries | **6,534** |
| Late Delivery Rate | **6.77%** |
| Customer Segments | **6** |
| Decision Scenarios | **162** |
| Interactive Dash Visualizations | **50** |
| Power BI Report Pages | **5** |

*All metrics reflect historical research data rather than live operational activity.*

---

## Business Problems Addressed

The platform investigates five connected business domains:

**01 — Business Performance**

How do order volume, merchandise value, and geographical contribution change over time? Which areas deserve greater management attention?

**02 — Customer Intelligence**

Which customers generate greater value? How do purchasing frequency, recency, customer segments, and cohort retention vary?

**03 — Operational Reliability**

Where are delivery delays concentrated? How do SLA outcomes differ across states, sellers, and delivery periods?

**04 — Predictive Risk Evaluation**

Can historical delivery lateness be predicted reliably? How do discrimination, precision-recall performance, calibration, and review capacity affect model usability?

**05 — Financial Decision Intelligence**

Under what cost and effectiveness assumptions might an intervention break even? Which hypothetical scenarios suggest unacceptable financial risk?

---

## Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| Data Storage | PostgreSQL, Docker | Relational data warehouse |
| Data Transformation | SQL, dbt | Data modeling, testing, KPI reconciliation |
| Data Analysis | Python, Pandas | EDA, segmentation, customer and operations analytics |
| Machine Learning | Scikit-learn | Delivery-risk modeling and chronological evaluation |
| Interactive Analytics | Plotly, Dash | Dynamic visualizations and decision exploration |
| Quality Assurance | Playwright, Python | Regression, browser and interaction testing |
| Version Control | Git | Reproducible development checkpoints |

---

## Platform Architecture

```text
                BRAZILIAN OLIST DATASET
                          |
                          v
                DATA INGESTION & QA
                       Python
                          |
                          v
                 POSTGRESQL WAREHOUSE
                          |
                          v
                    DBT + SQL MODELS
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
          CUSTOMER     DELIVERY    COMMERCIAL
          ANALYTICS    ANALYTICS   ANALYTICS
              |           |           |
              +-----------+-----------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
       MACHINE LEARNING        SCENARIO ENGINE
       MODEL EVALUATION       162 WHAT-IF CASES
              |                       |
              +-----------+-----------+
                          |
                          +
                          |
                          v
                     PLOTLY DASH
                     5 DASHBOARDS
                      50 CHARTS
```

---


### Plotly Dash — Interactive Intelligence Platform

The Dash application contains **five responsive pages and 50 interactive visualizations**.

| Dashboard | Visualizations | Analytical Focus |
|---|---:|---|
| Executive Command | 10 | Orders, sales trends, geographical performance, delivery outcomes |
| Customer Intelligence | 10 | RFM segments, repeat behavior, customer value, cohort retention |
| Operations & Logistics | 10 | Delivery SLAs, duration, freight, sellers and geography |
| Predictive Intelligence | 10 | Risk model evaluation, probability calibration and review capacity |
| Decision Scenario Lab | 10 | Hypothetical intervention economics, sensitivity and break-even |

The application features an enterprise-white interface, interactive filters, and responsive desktop, tablet and mobile layouts.

---

## Customer Analytics

APEX analyzes customer behavior through **six segments**, purchasing frequency, recency, monetary value, repeat activity, and acquisition cohorts.

The customer intelligence layer is designed to help investigate:

- Which customer groups contribute the greatest merchandise value?
- How do repeat-purchasing behaviors differ by segment?
- Which acquisition cohorts have observable repeat activity?
- Where might additional retention analysis be valuable?

Cohort analysis accounts for incomplete observation windows rather than treating unavailable future periods as zero retention.

---

## Predictive Analytics — Delivery Risk

A delivery-delay prediction model was evaluated using a **chronological holdout**, rather than relying only on random-split performance.

| Evaluation Metric | Result |
|---|---:|
| Held-Out Orders | 12,507 |
| Actual Late Cases | 601 |
| ROC-AUC | ~0.620 |
| Average Precision | ~0.080 |
| Deployment Recommendation | **Not Production-Ready** |

The evaluation includes discrimination, class imbalance, probability calibration, and operational review-capacity considerations.

**Key conclusion:** The available model evidence does not support deploying the classifier as an operational intervention system.

This distinction is intentional: APEX emphasizes honest model evaluation over unsupported claims of predictive accuracy.

---

## Decision Intelligence — 162 Financial Scenarios

The scenario engine analyzes **162 hypothetical intervention cases** using combinations of intervention assumptions, operational review capacity, effectiveness, costs, and expected value.

The analysis includes:

- Hypothetical intervention cost and benefit
- Net-value calculations
- Sensitivity analysis
- Capacity constraints
- Break-even thresholds
- GO/NO-GO decision framing

**Reference scenario:** R$−2,217.50 in hypothetical net value under the specified assumptions.

**Decision finding:** All six documented reference cases were negative, supporting a conditional NO-GO recommendation for those assumptions.

These values are **scenario estimates, not realized business savings or causal intervention effects**.

---

## Quality Assurance

The Dash implementation has undergone automated checks covering data reconciliation, visualization integrity, callbacks, responsive behavior and filter interactions.

| Quality Gate | Verified Result |
|---|---|
| Core dashboard regression suites | 11 passed |
| Unique chart count | 50 verified |
| Browser page/viewport checks | 15/15 passed |
| Plotly light-theme verification | 50/50 passed |
| Decision Lab filter interactions | Passed |
| Browser JavaScript errors | None detected |
| Document horizontal overflow | None detected in tested viewports |

The reported responsive tests cover desktop, tablet and mobile viewports.

---

## Running the Dash Application Locally

### Prerequisites

- Python 3.12 and project dependencies
- Docker and PostgreSQL
- Configured database environment
- Populated analytics warehouse

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/apex-ecommerce-decision-intelligence.git
cd apex-ecommerce-decision-intelligence
```

Replace `YOUR_USERNAME` with the actual GitHub account after publication.

### 2. Create the Python environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Configure the database

Use `.env.example` as a reference for the required settings and configure local credentials privately.

The analytical warehouse must be populated using the project's existing ingestion and dbt workflows before Dash can display its warehouse-backed results.

### 4. Start the application

```powershell
python src\dashboard\app.py
```

Then open:

**http://127.0.0.1:8050/**

---

## Project Structure

```text
ProjectAPEX/
|
+-- business/              Business requirements and KPI definitions
+-- config/                Project and dbt profile configuration
+-- database/              SQL migrations and analytical queries
+-- dbt/                   Staging models, marts and tests
+-- docs/                  Evidence, validation and research documentation
+-- src/
|   +-- analytics/         Statistical and customer analytics
|   +-- dashboard/         Dash application, charts, pages and CSS
|   +-- ingestion/         Source-data validation and ingestion
|   +-- modeling/          Predictive modeling and evaluation
+-- tests/                 Regression and browser tests
+-- requirements.txt       Python dependencies
+-- requirements-lock.txt  Locked dependency reference
+-- compose.yaml           Local container configuration
+-- README.md              Project documentation
```

---

## Business Value

APEX demonstrates how an analytics platform can move beyond static reporting:

**Raw data → Reliable metrics → Analytical investigation → Predictive evidence → Financial scenarios → Decision support**

The project enables users to investigate commercial performance, customer value, operational reliability and the feasibility of potential interventions.

Its business value lies in **traceable metrics, transparent analytical limitations and structured decision support**—not claims of observed revenue growth, cost savings, or production ML performance.

---

## Project Status

| Deliverable | Status |
|---|---|
| PostgreSQL warehouse and dbt transformations | Complete |
| Statistical and customer analytics | Complete |
| Delivery-risk model evaluation | Complete |
| Scenario modeling | Complete |
| Five-page Plotly Dash platform | Complete |
| Enterprise-white UI and automated Dash QA | Complete |

---

## Dataset Attribution

This project uses the historical Brazilian Olist e-commerce dataset for independent analytics portfolio research.

APEX is not affiliated with or endorsed by Olist.

---

## Final Perspective

> **APEX is built to demonstrate not just how to analyze data, but how to evaluate evidence, communicate uncertainty and support better business decisions.**

**APEX — Turning Data into Decision Intelligence.**
