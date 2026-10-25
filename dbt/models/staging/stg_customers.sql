SELECT
    customer_id,
    customer_unique_id,
    NULLIF(customer_zip_code_prefix, '')::integer AS customer_zip_code_prefix,
    customer_city,
    customer_state
FROM {{ source('olist_raw', 'olist_customers_dataset') }}
