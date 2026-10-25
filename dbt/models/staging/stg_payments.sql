SELECT
    order_id,
    NULLIF(payment_sequential, '')::integer AS payment_sequential,
    payment_type,
    NULLIF(payment_installments, '')::integer AS payment_installments,
    NULLIF(payment_value, '')::numeric AS payment_value
FROM {{ source('olist_raw', 'olist_order_payments_dataset') }}
