SELECT
    review_id,
    order_id,
    NULLIF(review_score, '')::integer AS review_score,
    NULLIF(review_comment_title, '') AS review_comment_title,
    NULLIF(review_comment_message, '') AS review_comment_message,
    NULLIF(review_creation_date, '')::timestamp AS review_creation_date,
    NULLIF(review_answer_timestamp, '')::timestamp AS review_answer_timestamp
FROM {{ source('olist_raw', 'olist_order_reviews_dataset') }}
