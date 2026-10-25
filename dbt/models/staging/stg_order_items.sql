SELECT
    order_id,
    NULLIF(order_item_id, '')::integer AS order_item_id,
    product_id,
    seller_id,
    NULLIF(shipping_limit_date, '')::timestamp AS shipping_limit_date,
    NULLIF(price, '')::numeric AS price,
    NULLIF(freight_value, '')::numeric AS freight_value
FROM {{ source('olist_raw', 'olist_order_items_dataset') }}
