CREATE OR REPLACE VIEW analytics.v_customer_cohort_activity AS
WITH delivered_orders AS (
    SELECT
        customer_unique_id,
        order_id,
        DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
        order_purchase_timestamp
    FROM analytics.v_order_intelligence
    WHERE order_status = 'delivered'
      AND customer_unique_id IS NOT NULL
      AND order_purchase_timestamp IS NOT NULL
),
customer_first AS (
    SELECT
        customer_unique_id,
        MIN(purchase_month) AS cohort_month
    FROM delivered_orders
    GROUP BY customer_unique_id
),
cohort_activity AS (
    SELECT
        f.cohort_month,
        d.purchase_month,
        (
            (EXTRACT(YEAR FROM d.purchase_month)::integer - EXTRACT(YEAR FROM f.cohort_month)::integer) * 12
            + EXTRACT(MONTH FROM d.purchase_month)::integer
            - EXTRACT(MONTH FROM f.cohort_month)::integer
        ) AS months_since_first,
        COUNT(DISTINCT d.customer_unique_id) AS active_customers
    FROM delivered_orders d
    JOIN customer_first f
        ON d.customer_unique_id = f.customer_unique_id
    GROUP BY 1, 2, 3
),
cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(*) AS cohort_size
    FROM customer_first
    GROUP BY cohort_month
),
boundary AS (
    SELECT
        MAX(order_purchase_timestamp)::date AS last_observed_date
    FROM analytics.v_order_intelligence
)
SELECT
    a.cohort_month,
    a.purchase_month,
    a.months_since_first,
    c.cohort_size,
    a.active_customers,
    ROUND(100.0 * a.active_customers / NULLIF(c.cohort_size, 0), 4) AS observed_activity_pct,
    (
        a.purchase_month + INTERVAL '1 month'
    )::date <= b.last_observed_date + 1 AS fully_observed_calendar_month
FROM cohort_activity a
JOIN cohort_sizes c
    ON a.cohort_month = c.cohort_month
CROSS JOIN boundary b;

CREATE OR REPLACE VIEW analytics.v_customer_cohort_retention AS
SELECT
    cohort_month,
    purchase_month,
    months_since_first,
    cohort_size,
    active_customers,
    observed_activity_pct
FROM analytics.v_customer_cohort_activity
WHERE fully_observed_calendar_month
  AND months_since_first BETWEEN 0 AND 12;
