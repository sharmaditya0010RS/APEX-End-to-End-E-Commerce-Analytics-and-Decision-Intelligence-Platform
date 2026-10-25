SELECT
    geolocation_zip_code_prefix,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY geolocation_lat::double precision) AS latitude,
    percentile_cont(0.5) WITHIN GROUP (ORDER BY geolocation_lng::double precision) AS longitude,
    COUNT(*) AS source_observations,
    COUNT(DISTINCT geolocation_lat::text || ',' || geolocation_lng::text) AS distinct_coordinate_pairs
FROM {{ ref('stg_geolocation') }}
WHERE geolocation_zip_code_prefix IS NOT NULL
GROUP BY geolocation_zip_code_prefix
