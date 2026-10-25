WITH model AS (
    SELECT
        *,
        CASE
            WHEN order_purchase_timestamp >= DATE '2017-01-01'
             AND order_purchase_timestamp < DATE '2018-05-01'
                THEN 'train'
            WHEN order_purchase_timestamp >= DATE '2018-05-01'
             AND order_purchase_timestamp < DATE '2018-07-01'
                THEN 'validation'
            WHEN order_purchase_timestamp >= DATE '2018-07-01'
             AND order_purchase_timestamp < DATE '2018-09-01'
                THEN 'test'
            ELSE 'excluded_boundary'
        END AS split
    FROM analytics.v_delivery_risk_features
)
SELECT
    split,
    COUNT(*) AS orders,
    SUM(target_late) AS late_orders,
    ROUND(
        100.0 * SUM(target_late) / NULLIF(COUNT(*), 0),
        4
    ) AS late_rate_pct
FROM model
GROUP BY split
ORDER BY split;

WITH checks AS (
    SELECT
        'Order grain' AS check_name,
        CASE WHEN COUNT(*) = COUNT(DISTINCT order_id)
            THEN 'PASS' ELSE 'FAIL' END AS result
    FROM analytics.v_delivery_risk_features

    UNION ALL

    SELECT
        'Full SLA reconciliation',
        CASE WHEN COUNT(*) = 96470
            THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_delivery_risk_features

    UNION ALL

    SELECT
        'Valid binary target',
        CASE WHEN COUNT(*) FILTER (
            WHERE target_late NOT IN (0,1)
               OR target_late IS NULL
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_delivery_risk_features

    UNION ALL

    SELECT
        'Nonnegative promised duration',
        CASE WHEN COUNT(*) FILTER (
            WHERE promised_delivery_days < 0
               OR promised_delivery_days IS NULL
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_delivery_risk_features

    UNION ALL

    SELECT
        'No missing geography',
        CASE WHEN COUNT(*) FILTER (
            WHERE customer_state IS NULL
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_delivery_risk_features

    UNION ALL

    SELECT
        'Late labels reconcile',
        CASE WHEN SUM(target_late) = 6534
            THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_delivery_risk_features
)
SELECT *
FROM checks
ORDER BY check_name;
