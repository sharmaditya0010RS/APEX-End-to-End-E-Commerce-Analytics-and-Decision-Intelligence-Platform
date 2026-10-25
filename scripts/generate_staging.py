from pathlib import Path

root = Path(__file__).resolve().parents[1]
staging = root / "dbt" / "models" / "staging"
staging.mkdir(parents=True, exist_ok=True)

models = {
    "orders": """
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
""",
    "order_items": """
SELECT
    order_id,
    NULLIF(order_item_id, '')::integer AS order_item_id,
    product_id,
    seller_id,
    NULLIF(shipping_limit_date, '')::timestamp AS shipping_limit_date,
    NULLIF(price, '')::numeric AS price,
    NULLIF(freight_value, '')::numeric AS freight_value
FROM {{ source('olist_raw', 'olist_order_items_dataset') }}
""",
    "payments": """
SELECT
    order_id,
    NULLIF(payment_sequential, '')::integer AS payment_sequential,
    payment_type,
    NULLIF(payment_installments, '')::integer AS payment_installments,
    NULLIF(payment_value, '')::numeric AS payment_value
FROM {{ source('olist_raw', 'olist_order_payments_dataset') }}
""",
    "reviews": """
SELECT
    review_id,
    order_id,
    NULLIF(review_score, '')::integer AS review_score,
    NULLIF(review_comment_title, '') AS review_comment_title,
    NULLIF(review_comment_message, '') AS review_comment_message,
    NULLIF(review_creation_date, '')::timestamp AS review_creation_date,
    NULLIF(review_answer_timestamp, '')::timestamp AS review_answer_timestamp
FROM {{ source('olist_raw', 'olist_order_reviews_dataset') }}
""",
    "customers": """
SELECT
    customer_id,
    customer_unique_id,
    NULLIF(customer_zip_code_prefix, '')::integer AS customer_zip_code_prefix,
    customer_city,
    customer_state
FROM {{ source('olist_raw', 'olist_customers_dataset') }}
""",
    "products": """
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
""",
    "sellers": """
SELECT
    seller_id,
    NULLIF(seller_zip_code_prefix, '')::integer AS seller_zip_code_prefix,
    seller_city,
    seller_state
FROM {{ source('olist_raw', 'olist_sellers_dataset') }}
""",
    "geolocation": """
SELECT
    NULLIF(geolocation_zip_code_prefix, '')::integer AS geolocation_zip_code_prefix,
    NULLIF(geolocation_lat, '')::numeric AS geolocation_lat,
    NULLIF(geolocation_lng, '')::numeric AS geolocation_lng,
    geolocation_city,
    geolocation_state
FROM {{ source('olist_raw', 'olist_geolocation_dataset') }}
""",
    "category_translation": """
SELECT
    product_category_name,
    product_category_name_english
FROM {{ source('olist_raw', 'product_category_name_translation') }}
"""
}

for name, query in models.items():
    (staging / f"stg_{name}.sql").write_text(
        query.strip() + "\n",
        encoding="utf-8"
    )

sources = [
    "olist_orders_dataset",
    "olist_order_items_dataset",
    "olist_order_payments_dataset",
    "olist_order_reviews_dataset",
    "olist_customers_dataset",
    "olist_products_dataset",
    "olist_sellers_dataset",
    "olist_geolocation_dataset",
    "product_category_name_translation"
]

source_yaml = "\n".join([
    "version: 2",
    "",
    "sources:",
    "  - name: olist_raw",
    "    schema: raw",
    "    tables:"
] + [f"      - name: {name}" for name in sources])

(staging / "sources.yml").write_text(source_yaml + "\n", encoding="utf-8")

print(f"Created {len(models)} staging models")
print(f"Registered {len(sources)} raw sources")
