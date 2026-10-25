SELECT
    NULLIF(geolocation_zip_code_prefix, '')::integer AS geolocation_zip_code_prefix,
    NULLIF(geolocation_lat, '')::numeric AS geolocation_lat,
    NULLIF(geolocation_lng, '')::numeric AS geolocation_lng,
    geolocation_city,
    geolocation_state
FROM {{ source('olist_raw', 'olist_geolocation_dataset') }}
