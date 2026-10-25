WITH actual AS (
    SELECT
        COUNT(*) AS total_orders,
        COUNT(*) FILTER (WHERE delivery_sla_eligible) AS eligible_orders,
        COUNT(*) FILTER (WHERE is_late_calendar) AS calendar_late,
        COUNT(*) FILTER (WHERE is_late_timestamp) AS timestamp_late
    FROM {{ ref('fact_orders') }}
)
SELECT *
FROM actual
WHERE total_orders <> 99441
   OR eligible_orders <> 96470
   OR calendar_late <> 6534
   OR timestamp_late <> 7826
