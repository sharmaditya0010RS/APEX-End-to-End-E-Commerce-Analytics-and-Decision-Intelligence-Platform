SELECT
    'All-order observation boundary' AS metric,
    MAX(order_purchase_timestamp)::text AS value
FROM analytics.v_order_intelligence

UNION ALL

SELECT
    'Last delivered-order purchase',
    MAX(order_purchase_timestamp)::text
FROM analytics.v_order_intelligence
WHERE order_status = 'delivered';

SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
    COUNT(*) AS all_orders,
    COUNT(*) FILTER (
        WHERE order_status = 'delivered'
    ) AS delivered_orders
FROM analytics.v_order_intelligence
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY 1
ORDER BY purchase_month DESC
LIMIT 8;

SELECT
    cohort_month,
    months_since_first,
    cohort_size,
    active_customers,
    observed_activity_pct,
    fully_observed
FROM analytics.v_customer_cohort_matrix
WHERE cohort_month >= DATE '2018-06-01'
  AND months_since_first BETWEEN 0 AND 6
ORDER BY cohort_month, months_since_first;
