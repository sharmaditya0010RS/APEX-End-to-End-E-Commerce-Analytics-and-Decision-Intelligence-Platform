SELECT
    p.product_id,
    p.product_category_name,
    COALESCE(t.product_category_name_english, 'Unknown') AS category_english,
    CASE
        WHEN p.product_category_name IS NULL THEN 'Missing'
        WHEN t.product_category_name_english IS NULL THEN 'Unmapped'
        ELSE 'Mapped'
    END AS category_mapping_status,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    p.product_photos_qty
FROM {{ ref('stg_products') }} p
LEFT JOIN {{ ref('stg_category_translation') }} t
    ON p.product_category_name = t.product_category_name
