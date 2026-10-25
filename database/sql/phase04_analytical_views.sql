CREATE SCHEMA IF NOT EXISTS analytics;

CREATE OR REPLACE VIEW analytics.v_order_intelligence AS
WITH reviews AS (
    SELECT
        order_id,
        AVG(review_score::numeric) AS average_review_score,
        COUNT(*) AS review_record_count
    FROM apex_marts.fact_reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_status,
    o.order_purchase_timestamp,
    DATE_TRUNC('month', o.order_purchase_timestamp)::date AS purchase_month,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    o.item_count,
    o.gross_item_value,
    o.freight_value,
    o.total_payment_value,
    o.payment_record_count,
    o.missing_payment_flag,
    o.delivery_sla_eligible,
    o.is_late_calendar,
    o.is_late_timestamp,
    CASE
        WHEN o.delivery_sla_eligible
        THEN EXTRACT(EPOCH FROM (
            o.order_delivered_customer_date - o.order_estimated_delivery_date
        )) / 86400.0
        ELSE NULL
    END AS delivery_difference_days,
    r.average_review_score,
    COALESCE(r.review_record_count, 0) AS review_record_count
FROM apex_marts.fact_orders o
JOIN apex_marts.dim_customers c
    ON o.customer_id = c.customer_id
LEFT JOIN reviews r
    ON o.order_id = r.order_id;

CREATE OR REPLACE VIEW analytics.v_seller_intelligence AS
WITH seller_orders AS (
    SELECT
        seller_id,
        order_id,
        SUM(price) AS seller_item_value,
        SUM(freight_value) AS seller_freight_value,
        COUNT(*) AS seller_item_count
    FROM apex_marts.fact_order_items
    GROUP BY seller_id, order_id
)
SELECT
    so.seller_id,
    so.order_id,
    s.seller_state,
    s.seller_city,
    so.seller_item_value,
    so.seller_freight_value,
    so.seller_item_count,
    o.order_purchase_timestamp,
    o.order_status,
    o.delivery_sla_eligible,
    o.is_late_calendar,
    o.average_review_score
FROM seller_orders so
JOIN analytics.v_order_intelligence o
    ON so.order_id = o.order_id
JOIN apex_marts.dim_sellers s
    ON so.seller_id = s.seller_id;

CREATE OR REPLACE VIEW analytics.v_customer_intelligence AS
WITH customer_orders AS (
    SELECT
        customer_unique_id,
        customer_state,
        order_id,
        order_purchase_timestamp,
        gross_item_value,
        order_status
    FROM analytics.v_order_intelligence
    WHERE customer_unique_id IS NOT NULL
),
customer_aggregates AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS lifetime_order_count,
        COUNT(DISTINCT order_id) FILTER (
            WHERE order_status = 'delivered'
        ) AS delivered_order_count,
        MIN(order_purchase_timestamp) AS first_purchase,
        MAX(order_purchase_timestamp) AS last_purchase,
        SUM(gross_item_value) AS observed_item_value
    FROM customer_orders
    GROUP BY customer_unique_id
)
SELECT
    customer_unique_id,
    lifetime_order_count,
    delivered_order_count,
    first_purchase,
    last_purchase,
    observed_item_value,
    DATE_TRUNC('month', first_purchase)::date AS acquisition_cohort
FROM customer_aggregates;
