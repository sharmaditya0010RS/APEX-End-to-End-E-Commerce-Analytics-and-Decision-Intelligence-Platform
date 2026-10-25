SELECT
    order_id,
    customer_id,
    order_status,
    NULLIF(order_purchase_timestamp, '')::timestamp AS order_purchase_timestamp,
    NULLIF(order_approved_at, '')::timestamp AS order_approved_at,
    NULLIF(order_delivered_carrier_date, '')::timestamp AS order_delivered_carrier_date,
    NULLIF(order_delivered_customer_date, '')::timestamp AS order_delivered_customer_date,
    NULLIF(order_estimated_delivery_date, '')::timestamp AS order_estimated_delivery_date
FROM {{ source('olist_raw', 'olist_orders_dataset') }}
