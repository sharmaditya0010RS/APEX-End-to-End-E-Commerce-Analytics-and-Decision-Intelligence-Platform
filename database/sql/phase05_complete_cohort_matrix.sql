CREATE OR REPLACE VIEW analytics.v_customer_cohort_matrix AS
WITH cohort_sizes AS (
    SELECT
        cohort_month,
        cohort_size
    FROM analytics.v_customer_cohort_activity
    WHERE months_since_first = 0
),
observation AS (
    SELECT
        MAX(order_purchase_timestamp)::date AS last_observed_date
    FROM analytics.v_order_intelligence
    WHERE order_status = 'delivered'
      AND order_purchase_timestamp IS NOT NULL
),
grid AS (
    SELECT
        c.cohort_month,
        c.cohort_size,
        offset_month.months_since_first,
        (
            c.cohort_month
            + offset_month.months_since_first * INTERVAL '1 month'
        )::date AS purchase_month,
        o.last_observed_date
    FROM cohort_sizes c
    CROSS JOIN generate_series(0, 12) AS offset_month(months_since_first)
    CROSS JOIN observation o
)
SELECT
    g.cohort_month,
    g.purchase_month,
    g.months_since_first,
    g.cohort_size,
    CASE
        WHEN g.purchase_month + INTERVAL '1 month'
             <= g.last_observed_date + INTERVAL '1 day'
        THEN COALESCE(a.active_customers, 0)
        ELSE NULL
    END AS active_customers,
    CASE
        WHEN g.purchase_month + INTERVAL '1 month'
             <= g.last_observed_date + INTERVAL '1 day'
        THEN ROUND(
            100.0 * COALESCE(a.active_customers, 0)
            / NULLIF(g.cohort_size, 0),
            4
        )
        ELSE NULL
    END AS observed_activity_pct,
    (
        g.purchase_month + INTERVAL '1 month'
        <= g.last_observed_date + INTERVAL '1 day'
    ) AS fully_observed
FROM grid g
LEFT JOIN analytics.v_customer_cohort_activity a
    ON g.cohort_month = a.cohort_month
   AND g.months_since_first = a.months_since_first;
