SELECT
    DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
    COUNT(*) AS eligible_orders,
    COUNT(*) FILTER (WHERE is_late_calendar) AS late_orders,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE is_late_calendar)
        / NULLIF(COUNT(*), 0),
        3
    ) AS late_rate_pct
FROM analytics.v_order_intelligence
WHERE delivery_sla_eligible = TRUE
GROUP BY 1
ORDER BY 1;

SELECT
    COUNT(*) AS eligible_orders,
    COUNT(*) FILTER (
        WHERE order_purchase_timestamp IS NULL
    ) AS missing_purchase_timestamp,
    COUNT(*) FILTER (
        WHERE order_estimated_delivery_date IS NULL
    ) AS missing_promised_date,
    COUNT(*) FILTER (
        WHERE customer_state IS NULL
    ) AS missing_customer_state,
    COUNT(*) FILTER (
        WHERE gross_item_value IS NULL
    ) AS missing_item_value,
    COUNT(*) FILTER (
        WHERE item_count IS NULL
    ) AS missing_item_count,
    COUNT(DISTINCT customer_unique_id) AS unique_customers
FROM analytics.v_order_intelligence
WHERE delivery_sla_eligible = TRUE;

SELECT
    COUNT(*) AS eligible_orders,
    COUNT(*) FILTER (
        WHERE order_estimated_delivery_date < order_purchase_timestamp
    ) AS promise_before_purchase,
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                order_estimated_delivery_date - order_purchase_timestamp
            )) / 86400.0
        ),
        2
    ) AS mean_promised_days
FROM analytics.v_order_intelligence
WHERE delivery_sla_eligible = TRUE;
