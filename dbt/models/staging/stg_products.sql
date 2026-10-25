SELECT
    product_id,
    product_category_name,
    NULLIF(product_name_lenght, '')::integer AS product_name_length,
    NULLIF(product_description_lenght, '')::integer AS product_description_length,
    NULLIF(product_photos_qty, '')::integer AS product_photos_qty,
    NULLIF(product_weight_g, '')::numeric AS product_weight_g,
    NULLIF(product_length_cm, '')::numeric AS product_length_cm,
    NULLIF(product_height_cm, '')::numeric AS product_height_cm,
    NULLIF(product_width_cm, '')::numeric AS product_width_cm
FROM {{ source('olist_raw', 'olist_products_dataset') }}
