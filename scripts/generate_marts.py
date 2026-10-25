from pathlib import Path

root = Path(__file__).resolve().parents[1]
marts = root / "dbt" / "models" / "marts"
marts.mkdir(parents=True, exist_ok=True)

models = {
    "dim_customers": """
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM {{ ref('stg_customers') }}
""",
    "dim_products": """
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
""",
    "dim_sellers": """
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM {{ ref('stg_sellers') }}
""",
    "dim_geography": """
SELECT
    geolocation_zip_code_prefix,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY geolocation_lat::double precision) AS latitude,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY geolocation_lng::double precision) AS longitude,
    COUNT(*) AS source_observations,
    COUNT(DISTINCT geolocation_lat::text || ',' || geolocation_lng::text) AS distinct_coordinate_pairs
FROM {{ ref('stg_geolocation') }}
WHERE geolocation_zip_code_prefix IS NOT NULL
GROUP BY geolocation_zip_code_prefix
""",
    "fact_orders": """
WITH payments AS (
    SELECT
        order_id,
        COUNT(*) AS payment_record_count,
        SUM(payment_value) AS total_payment_value
    FROM {{ ref('stg_payments') }}
    GROUP BY order_id
),
items AS (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS gross_item_value,
        SUM(freight_value) AS freight_value
    FROM {{ ref('stg_order_items') }}
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    COALESCE(i.item_count, 0) AS item_count,
    i.gross_item_value,
    i.freight_value,
    p.total_payment_value,
    COALESCE(p.payment_record_count, 0) AS payment_record_count,
    CASE WHEN p.order_id IS NULL THEN TRUE ELSE FALSE END AS missing_payment_flag,
    CASE
        WHEN o.order_status = 'delivered'
         AND o.order_delivered_customer_date IS NOT NULL
         AND o.order_estimated_delivery_date IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END AS delivery_sla_eligible,
    CASE
        WHEN o.order_status = 'delivered'
         AND o.order_delivered_customer_date IS NOT NULL
         AND o.order_estimated_delivery_date IS NOT NULL
        THEN o.order_delivered_customer_date::date > o.order_estimated_delivery_date::date
        ELSE NULL
    END AS is_late_calendar,
    CASE
        WHEN o.order_status = 'delivered'
         AND o.order_delivered_customer_date IS NOT NULL
         AND o.order_estimated_delivery_date IS NOT NULL
        THEN o.order_delivered_customer_date > o.order_estimated_delivery_date
        ELSE NULL
    END AS is_late_timestamp
FROM {{ ref('stg_orders') }} o
LEFT JOIN items i ON o.order_id = i.order_id
LEFT JOIN payments p ON o.order_id = p.order_id
""",
    "fact_order_items": """
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
FROM {{ ref('stg_order_items') }}
""",
    "fact_payments": """
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM {{ ref('stg_payments') }}
""",
    "fact_reviews": """
SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date,
    review_answer_timestamp
FROM {{ ref('stg_reviews') }}
"""
}

for name, statement in models.items():
    (marts / f"{name}.sql").write_text(
        statement.strip() + "\n",
        encoding="utf-8"
    )

print(f"Created {len(models)} warehouse marts")
