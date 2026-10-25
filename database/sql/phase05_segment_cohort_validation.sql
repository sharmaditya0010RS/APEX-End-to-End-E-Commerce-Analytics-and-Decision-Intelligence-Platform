WITH checks AS (
    SELECT
        'Segment customer grain' AS check_name,
        CASE WHEN COUNT(*) = COUNT(DISTINCT customer_unique_id)
            THEN 'PASS' ELSE 'FAIL' END AS result
    FROM analytics.v_customer_segments

    UNION ALL

    SELECT
        'All customers assigned to one segment',
        CASE WHEN COUNT(*) FILTER (WHERE customer_segment IS NULL) = 0
            THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_segments

    UNION ALL

    SELECT
        'Segment customer totals reconcile',
        CASE WHEN
            (SELECT SUM(customers) FROM analytics.v_customer_segment_summary)
            =
            (SELECT COUNT(*) FROM analytics.v_customer_rfm)
            THEN 'PASS' ELSE 'FAIL' END

    UNION ALL

    SELECT
        'Segment monetary totals reconcile',
        CASE WHEN
            (SELECT SUM(gross_item_value) FROM analytics.v_customer_segment_summary)
            IS NOT DISTINCT FROM
            (SELECT SUM(monetary_value) FROM analytics.v_customer_rfm)
            THEN 'PASS' ELSE 'FAIL' END

    UNION ALL

    SELECT
        'Segment delivered orders reconcile',
        CASE WHEN
            (SELECT SUM(delivered_orders) FROM analytics.v_customer_segment_summary)
            =
            (SELECT SUM(frequency) FROM analytics.v_customer_rfm)
            THEN 'PASS' ELSE 'FAIL' END

    UNION ALL

    SELECT
        'Cohort month zero matches cohort size',
        CASE WHEN COUNT(*) FILTER (
            WHERE months_since_first = 0
              AND active_customers <> cohort_size
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_activity

    UNION ALL

    SELECT
        'No cohort activity above cohort size',
        CASE WHEN COUNT(*) FILTER (
            WHERE active_customers > cohort_size
               OR active_customers < 1
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_activity

    UNION ALL

    SELECT
        'No negative cohort offsets',
        CASE WHEN COUNT(*) FILTER (
            WHERE months_since_first < 0
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_activity
)
SELECT *
FROM checks
ORDER BY check_name;

SELECT *
FROM analytics.v_customer_segment_summary
ORDER BY customers DESC;

SELECT
    cohort_month,
    months_since_first,
    cohort_size,
    active_customers,
    observed_activity_pct
FROM analytics.v_customer_cohort_retention
WHERE months_since_first IN (0, 1, 3, 6)
ORDER BY cohort_month, months_since_first
LIMIT 40;
