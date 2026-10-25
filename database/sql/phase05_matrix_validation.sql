WITH checks AS (
    SELECT
        'Unique cohort-month combinations' AS check_name,
        CASE
            WHEN COUNT(*) = COUNT(DISTINCT (cohort_month, months_since_first))
            THEN 'PASS' ELSE 'FAIL'
        END AS result
    FROM analytics.v_customer_cohort_matrix

    UNION ALL

    SELECT
        'No negative activity',
        CASE WHEN COUNT(*) FILTER (
            WHERE active_customers < 0
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_matrix

    UNION ALL

    SELECT
        'Activity never exceeds cohort size',
        CASE WHEN COUNT(*) FILTER (
            WHERE active_customers > cohort_size
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_matrix

    UNION ALL

    SELECT
        'Unobserved months remain null',
        CASE WHEN COUNT(*) FILTER (
            WHERE NOT fully_observed
              AND (active_customers IS NOT NULL OR observed_activity_pct IS NOT NULL)
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_matrix

    UNION ALL

    SELECT
        'Observed months are nonnull',
        CASE WHEN COUNT(*) FILTER (
            WHERE fully_observed
              AND (active_customers IS NULL OR observed_activity_pct IS NULL)
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_matrix

    UNION ALL

    SELECT
        'Month zero reconciles when fully observed',
        CASE WHEN COUNT(*) FILTER (
            WHERE months_since_first = 0
              AND fully_observed
              AND active_customers <> cohort_size
        ) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM analytics.v_customer_cohort_matrix

    UNION ALL

    SELECT
        'Each cohort has thirteen month slots',
        CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM (
        SELECT cohort_month
        FROM analytics.v_customer_cohort_matrix
        GROUP BY cohort_month
        HAVING COUNT(*) <> 13
    ) problems
)
SELECT * FROM checks ORDER BY check_name;

SELECT
    COUNT(*) AS matrix_cells,
    COUNT(*) FILTER (WHERE fully_observed) AS observable_cells,
    COUNT(*) FILTER (
        WHERE fully_observed AND active_customers = 0
    ) AS true_zero_cells,
    COUNT(*) FILTER (WHERE NOT fully_observed) AS censored_cells
FROM analytics.v_customer_cohort_matrix;
