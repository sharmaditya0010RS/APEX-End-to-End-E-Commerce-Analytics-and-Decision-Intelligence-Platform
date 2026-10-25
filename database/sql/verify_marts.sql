SELECT 'dim_customers' AS model, COUNT(*) AS rows FROM apex_marts.dim_customers
UNION ALL
SELECT 'dim_products', COUNT(*) FROM apex_marts.dim_products
UNION ALL
SELECT 'dim_sellers', COUNT(*) FROM apex_marts.dim_sellers
UNION ALL
SELECT 'dim_geography', COUNT(*) FROM apex_marts.dim_geography
UNION ALL
SELECT 'fact_orders', COUNT(*) FROM apex_marts.fact_orders
UNION ALL
SELECT 'fact_order_items', COUNT(*) FROM apex_marts.fact_order_items
UNION ALL
SELECT 'fact_payments', COUNT(*) FROM apex_marts.fact_payments
UNION ALL
SELECT 'fact_reviews', COUNT(*) FROM apex_marts.fact_reviews
ORDER BY model;
