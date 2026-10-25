WITH checks AS (
    SELECT
        'Unique customer grain' AS check_name,
        CASE
            WHEN COUNT(*) = COUNT(DISTINCT customer_unique_id)
            THEN 'PASS' ELSE 'FAIL'
        END AS result
    FROM analytics.v_customer_rfm

    UNION ALL

    SELECT
        'No null customer identities',
        CASE
            WHEN COUNT(*) FILTER (WHERE customer_unique_id IS NULL) = 0
            THEN 'PASS' ELSE 'FAIL'
        END
    FROM analytics.v_customer_rfm

    UNION ALL

    SELECT
        'Valid recency values',
        CASE
            WHEN COUNT(*) FILTER (WHERE recency_days < 0 OR recency_days IS NULL) = 0
            THEN 'PASS' ELSE 'FAIL'
        END
    FROM analytics.v_customer_rfm

    UNION ALL

    SELECT
        'Positive purchase frequency',
        CASE
            WHEN COUNT(*) FILTER (WHERE frequency < 1) = 0
            THEN 'PASS' ELSE 'FAIL'
        END
    FROM analytics.v_customer_rfm

    UNION ALL

    SELECT
        'Delivered order count reconciliation',
        CASE
            WHEN (SELECT SUM(frequency) FROM analytics.v_customer_rfm) =
                 (SELECT COUNT(*) FROM analytics.v_order_intelligence
                  WHERE order_status = 'delivered'
                    AND customer_unique_id IS NOT NULL
                    AND order_purchase_timestamp IS NOT NULL)
            THEN 'PASS' ELSE 'FAIL'
        END

    UNION ALL

    SELECT
        'Delivered item value reconciliation',
        CASE
            WHEN (SELECT SUM(monetary_value) FROM analytics.v_customer_rfm) IS NOT DISTINCT FROM
                 (SELECT SUM(gross_item_value)
                  FROM analytics.v_order_intelligence
                  WHERE order_status = 'delivered'
                    AND customer_unique_id IS NOT NULL
                    AND order_purchase_timestamp IS NOT NULL)
            THEN 'PASS' ELSE 'FAIL'
        END
)
SELECT * FROM checks ORDER BY check_name;

SELECT
    COUNT(*) AS customers,
    SUM(frequency) AS delivered_orders,
    COUNT(*) FILTER (WHERE repeat_customer_flag) AS repeat_customers,
    ROUND(100.0 * COUNT(*) FILTER (WHERE repeat_customer_flag) /
        NULLIF(COUNT(*), 0), 3) AS repeat_customer_pct,
    ROUND(AVG(recency_days), 2) AS average_recency_days,
    ROUND(SUM(monetary_value), 2) AS delivered_gross_item_value
FROM analytics.v_customer_rfm;
