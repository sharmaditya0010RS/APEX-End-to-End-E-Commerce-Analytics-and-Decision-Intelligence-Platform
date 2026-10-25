CREATE OR REPLACE VIEW analytics.v_customer_rfm AS
WITH observation AS (
    SELECT
        MAX(order_purchase_timestamp::date) + 1 AS analysis_date
    FROM analytics.v_order_intelligence
    WHERE order_status = 'delivered'
      AND order_purchase_timestamp IS NOT NULL
),
eligible_orders AS (
    SELECT
        customer_unique_id,
        order_id,
        order_purchase_timestamp,
        gross_item_value
    FROM analytics.v_order_intelligence
    WHERE order_status = 'delivered'
      AND customer_unique_id IS NOT NULL
      AND order_purchase_timestamp IS NOT NULL
),
customer_aggregates AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(gross_item_value) AS monetary_value,
        MIN(order_purchase_timestamp)::date AS first_purchase_date,
        MAX(order_purchase_timestamp)::date AS last_purchase_date
    FROM eligible_orders
    GROUP BY customer_unique_id
),
rfm_base AS (
    SELECT
        c.customer_unique_id,
        o.analysis_date,
        o.analysis_date - c.last_purchase_date AS recency_days,
        c.frequency,
        c.monetary_value,
        c.first_purchase_date,
        c.last_purchase_date
    FROM customer_aggregates c
    CROSS JOIN observation o
)
SELECT
    customer_unique_id,
    analysis_date,
    recency_days,
    frequency,
    monetary_value,
    first_purchase_date,
    last_purchase_date,
    CASE WHEN frequency >= 2 THEN TRUE ELSE FALSE END AS repeat_customer_flag
FROM rfm_base;
