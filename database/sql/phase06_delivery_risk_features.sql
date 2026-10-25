CREATE OR REPLACE VIEW analytics.v_delivery_risk_features AS
SELECT
    order_id,
    order_purchase_timestamp,
    DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
    customer_state,
    EXTRACT(MONTH FROM order_purchase_timestamp)::integer AS purchase_month_number,
    EXTRACT(DOW FROM order_purchase_timestamp)::integer AS purchase_day_of_week,
    EXTRACT(HOUR FROM order_purchase_timestamp)::integer AS purchase_hour,
    EXTRACT(EPOCH FROM (
        order_estimated_delivery_date - order_purchase_timestamp
    )) / 86400.0 AS promised_delivery_days,
    gross_item_value,
    freight_value,
    item_count,
    is_late_calendar::integer AS target_late
FROM analytics.v_order_intelligence
WHERE delivery_sla_eligible = TRUE
  AND order_purchase_timestamp IS NOT NULL
  AND order_estimated_delivery_date IS NOT NULL
  AND is_late_calendar IS NOT NULL;
