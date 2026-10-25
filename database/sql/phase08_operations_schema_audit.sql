SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'analytics'
  AND table_name IN (
      'v_order_intelligence',
      'v_seller_intelligence',
      'v_customer_intelligence'
  )
ORDER BY table_name, ordinal_position;

SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'apex_marts'
  AND table_name IN (
      'fact_orders',
      'fact_order_items',
      'fact_payments',
      'fact_reviews',
      'dim_sellers',
      'dim_geography'
  )
ORDER BY table_name, ordinal_position;
