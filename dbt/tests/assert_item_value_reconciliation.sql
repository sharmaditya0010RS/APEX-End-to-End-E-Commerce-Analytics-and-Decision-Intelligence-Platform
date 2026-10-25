WITH source_values AS (
    SELECT
        COUNT(*) AS item_rows,
        SUM(price) AS item_value,
        SUM(freight_value) AS freight_value
    FROM {{ ref('stg_order_items') }}
),
mart_values AS (
    SELECT
        COUNT(*) AS item_rows,
        SUM(price) AS item_value,
        SUM(freight_value) AS freight_value
    FROM {{ ref('fact_order_items') }}
)
SELECT
    source_values.item_rows AS source_rows,
    mart_values.item_rows AS mart_rows,
    source_values.item_value AS source_item_value,
    mart_values.item_value AS mart_item_value
FROM source_values
CROSS JOIN mart_values
WHERE source_values.item_rows <> mart_values.item_rows
   OR source_values.item_value IS DISTINCT FROM mart_values.item_value
   OR source_values.freight_value IS DISTINCT FROM mart_values.freight_value
