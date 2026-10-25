SELECT
    seller_id,
    NULLIF(seller_zip_code_prefix, '')::integer AS seller_zip_code_prefix,
    seller_city,
    seller_state
FROM {{ source('olist_raw', 'olist_sellers_dataset') }}
