WITH checks AS (
    SELECT
        'Order view grain' AS check_name,
        (SELECT COUNT(*) FROM analytics.v_order_intelligence) AS actual,
        99441::bigint AS expected
    UNION ALL
    SELECT
        'Unique orders',
        COUNT(DISTINCT order_id),
        99441
    FROM analytics.v_order_intelligence
    UNION ALL
    SELECT
        'Seller-order value reconciliation',
        CASE
            WHEN (
                SELECT SUM(seller_item_value)
                FROM analytics.v_seller_intelligence
            ) = (
                SELECT SUM(price)
                FROM apex_marts.fact_order_items
            ) THEN 1 ELSE 0 END,
        1
    UNION ALL
    SELECT
        'Calendar late deliveries',
        COUNT(*) FILTER (WHERE is_late_calendar),
        6534
    FROM analytics.v_order_intelligence
    UNION ALL
    SELECT
        'Eligible deliveries',
        COUNT(*) FILTER (WHERE delivery_sla_eligible),
        96470
    FROM analytics.v_order_intelligence
)
SELECT *,
    CASE WHEN actual = expected THEN 'PASS' ELSE 'FAIL' END AS result
FROM checks;
