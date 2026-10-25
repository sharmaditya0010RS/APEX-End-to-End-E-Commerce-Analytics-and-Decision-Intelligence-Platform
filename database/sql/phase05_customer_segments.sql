CREATE OR REPLACE VIEW analytics.v_customer_segments AS
WITH thresholds AS (
    SELECT
        percentile_cont(0.5) WITHIN GROUP (ORDER BY recency_days) AS median_recency,
        percentile_cont(0.5) WITHIN GROUP (ORDER BY monetary_value::double precision) AS median_monetary
    FROM analytics.v_customer_rfm
)
SELECT
    r.*,
    t.median_recency,
    t.median_monetary,
    CASE
        WHEN r.frequency >= 2
         AND r.recency_days <= t.median_recency
         AND r.monetary_value > t.median_monetary
            THEN 'Repeat Champions'
        WHEN r.frequency >= 2
         AND r.recency_days <= t.median_recency
            THEN 'Recent Repeat'
        WHEN r.frequency >= 2
            THEN 'Established Repeat'
        WHEN r.monetary_value > t.median_monetary
            THEN 'High-Value One-Time'
        WHEN r.recency_days <= t.median_recency
            THEN 'Recent One-Time'
        ELSE 'Dormant One-Time'
    END AS customer_segment
FROM analytics.v_customer_rfm r
CROSS JOIN thresholds t;

CREATE OR REPLACE VIEW analytics.v_customer_segment_summary AS
SELECT
    customer_segment,
    COUNT(*) AS customers,
    SUM(frequency) AS delivered_orders,
    SUM(monetary_value) AS gross_item_value,
    ROUND(AVG(monetary_value), 2) AS mean_customer_value,
    ROUND(AVG(recency_days), 2) AS mean_recency_days
FROM analytics.v_customer_segments
GROUP BY customer_segment;
