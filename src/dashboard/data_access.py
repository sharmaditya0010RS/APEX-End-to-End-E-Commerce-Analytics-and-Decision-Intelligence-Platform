from pathlib import Path
import os

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.getenv("POSTGRES_PORT", "5433")),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        options="-c max_parallel_workers_per_gather=0 -c work_mem=16MB",
        connect_timeout=10
    )

def executive_kpis():
    query = """
    SELECT
        COUNT(*) AS total_orders,
        COUNT(DISTINCT customer_unique_id) AS unique_customers,
        COALESCE(SUM(gross_item_value), 0) AS gross_item_value,
        COUNT(*) FILTER (WHERE delivery_sla_eligible) AS eligible_orders,
        COUNT(*) FILTER (
            WHERE delivery_sla_eligible AND is_late_calendar
        ) AS late_orders
    FROM analytics.v_order_intelligence
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()

    orders, customers, gross, eligible, late = row

    return {
        "total_orders": int(orders),
        "unique_customers": int(customers),
        "gross_item_value": float(gross),
        "eligible_orders": int(eligible),
        "late_orders": int(late),
        "late_rate": float(late / eligible) if eligible else 0.0
    }

def executive_monthly_trends(start_date, end_date):
    from datetime import date

    start = date.fromisoformat(str(start_date)[:10])
    end = date.fromisoformat(str(end_date)[:10])

    if start > end:
        raise ValueError("Start date cannot exceed end date")

    query = """
    SELECT
        DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
        COUNT(*) AS total_orders,
        COALESCE(SUM(gross_item_value), 0) AS gross_item_value,
        COUNT(*) FILTER (WHERE delivery_sla_eligible) AS eligible_orders,
        COUNT(*) FILTER (
            WHERE delivery_sla_eligible AND is_late_calendar
        ) AS late_orders
    FROM analytics.v_order_intelligence
    WHERE order_purchase_timestamp >= %s
      AND order_purchase_timestamp < (%s::date + INTERVAL '1 day')
    GROUP BY 1
    ORDER BY 1
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (start, end))
            rows = cursor.fetchall()

    return [
        {
            "month": row[0].isoformat(),
            "orders": int(row[1]),
            "gross_item_value": float(row[2]),
            "eligible_orders": int(row[3]),
            "late_orders": int(row[4]),
            "late_rate_pct": (
                100.0 * int(row[4]) / int(row[3])
                if row[3] else None
            )
        }
        for row in rows
    ]

def executive_breakdowns(start_date, end_date):
    from datetime import date

    start = date.fromisoformat(str(start_date)[:10])
    end = date.fromisoformat(str(end_date)[:10])

    if start > end:
        raise ValueError("Invalid purchase-date interval")

    filter_sql = """
    FROM analytics.v_order_intelligence
    WHERE order_purchase_timestamp >= %s
      AND order_purchase_timestamp < (%s::date + INTERVAL '1 day')
    """

    queries = {
        "status": """
            SELECT order_status, COUNT(*) AS orders
        """ + filter_sql + """
            GROUP BY order_status
            ORDER BY orders DESC, order_status
        """,
        "states": """
            SELECT customer_state,
                   COUNT(*) AS orders,
                   COALESCE(SUM(gross_item_value), 0) AS item_value
        """ + filter_sql + """
            GROUP BY customer_state
            ORDER BY orders DESC, customer_state
        """,
        "basket": """
            SELECT
                CASE
                    WHEN item_count = 1 THEN '1 item'
                    WHEN item_count = 2 THEN '2 items'
                    WHEN item_count = 3 THEN '3 items'
                    WHEN item_count BETWEEN 4 AND 5 THEN '4–5 items'
                    WHEN item_count >= 6 THEN '6+ items'
                    ELSE 'Unknown'
                END AS basket_group,
                COUNT(*) AS orders
        """ + filter_sql + """
            GROUP BY 1
        """,
        "monthly": """
            SELECT
                DATE_TRUNC('month', order_purchase_timestamp)::date,
                COUNT(*),
                COALESCE(SUM(gross_item_value), 0),
                COALESCE(SUM(freight_value), 0)
        """ + filter_sql + """
            GROUP BY 1
            ORDER BY 1
        """
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            results = {}
            for name, query in queries.items():
                cursor.execute(query, (start, end))
                results[name] = cursor.fetchall()

    return {
        "status": [
            {"status": str(name), "orders": int(count)}
            for name, count in results["status"]
        ],
        "states": [
            {
                "state": str(state) if state is not None else "Unknown",
                "orders": int(orders),
                "item_value": float(value)
            }
            for state, orders, value in results["states"]
        ],
        "basket": [
            {"group": str(group), "orders": int(count)}
            for group, count in results["basket"]
        ],
        "monthly": [
            {
                "month": month.isoformat(),
                "orders": int(count),
                "item_value": float(value),
                "freight_value": float(freight)
            }
            for month, count, value, freight in results["monthly"]
        ]
    }

def customer_intelligence_data():
    queries = {
        "segments": """
            SELECT
                customer_segment,
                customers,
                delivered_orders,
                gross_item_value,
                mean_customer_value,
                mean_recency_days
            FROM analytics.v_customer_segment_summary
            ORDER BY customers DESC, customer_segment
        """,
        "cohorts": """
            SELECT
                cohort_month,
                months_since_first,
                cohort_size,
                active_customers,
                observed_activity_pct,
                fully_observed
            FROM analytics.v_customer_cohort_matrix
            ORDER BY cohort_month, months_since_first
        """
    }

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(queries["segments"])
            segments = cursor.fetchall()

            cursor.execute(queries["cohorts"])
            cohorts = cursor.fetchall()

    return {
        "segments": [
            {
                "segment": str(row[0]),
                "customers": int(row[1]),
                "orders": int(row[2]),
                "gross_value": float(row[3]),
                "mean_value": float(row[4]),
                "mean_recency": float(row[5])
            }
            for row in segments
        ],
        "cohorts": [
            {
                "cohort": row[0].isoformat(),
                "month_offset": int(row[1]),
                "cohort_size": int(row[2]),
                "active_customers": (
                    int(row[3]) if row[3] is not None else None
                ),
                "activity_pct": (
                    float(row[4]) if row[4] is not None else None
                ),
                "observable": bool(row[5])
            }
            for row in cohorts
        ]
    }

def customer_rfm_distributions(selected_segment="all"):
    valid = {"all"}
    valid.update(
        row["segment"] for row in customer_intelligence_data()["segments"]
    )

    if selected_segment not in valid:
        raise ValueError("Unknown customer segment")

    query = """
    WITH base AS (
        SELECT
            frequency,
            recency_days,
            monetary_value
        FROM analytics.v_customer_segments
        WHERE (%s = 'all' OR customer_segment = %s)
    ),
    buckets AS (
        SELECT
            'frequency' AS dimension,
            CASE
                WHEN frequency = 1 THEN '1 order'
                WHEN frequency = 2 THEN '2 orders'
                WHEN frequency = 3 THEN '3 orders'
                ELSE '4+ orders'
            END AS bucket
        FROM base

        UNION ALL

        SELECT
            'recency',
            CASE
                WHEN recency_days <= 90 THEN '0–90 days'
                WHEN recency_days <= 180 THEN '91–180 days'
                WHEN recency_days <= 365 THEN '181–365 days'
                ELSE '366+ days'
            END
        FROM base

        UNION ALL

        SELECT
            'monetary',
            CASE
                WHEN monetary_value < 50 THEN 'Below R$50'
                WHEN monetary_value < 150 THEN 'R$50–149'
                WHEN monetary_value < 500 THEN 'R$150–499'
                ELSE 'R$500+'
            END
        FROM base
    )
    SELECT dimension, bucket, COUNT(*)
    FROM buckets
    GROUP BY dimension, bucket
    ORDER BY dimension, bucket
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (selected_segment, selected_segment))
            rows = cursor.fetchall()

    result = {
        "frequency": {},
        "recency": {},
        "monetary": {}
    }

    for dimension, bucket, count in rows:
        result[dimension][bucket] = int(count)

    return result

def operations_states():
    query = """
    SELECT DISTINCT customer_state
    FROM analytics.v_order_intelligence
    WHERE delivery_sla_eligible = TRUE
      AND customer_state IS NOT NULL
    ORDER BY customer_state
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]


def operations_delivery_data(start_date, end_date, state="all"):
    from datetime import date

    start = date.fromisoformat(str(start_date)[:10])
    end = date.fromisoformat(str(end_date)[:10])

    if start > end:
        raise ValueError("Start date cannot exceed end date")

    states = operations_states()

    if state != "all" and state not in states:
        raise ValueError("Unknown customer state")

    source = """
    WITH base AS (
        SELECT
            order_id,
            DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
            is_late_calendar,
            EXTRACT(EPOCH FROM (
                order_delivered_customer_date - order_purchase_timestamp
            )) / 86400.0 AS actual_days,
            EXTRACT(EPOCH FROM (
                order_estimated_delivery_date - order_purchase_timestamp
            )) / 86400.0 AS promised_days
        FROM analytics.v_order_intelligence
        WHERE delivery_sla_eligible = TRUE
          AND order_purchase_timestamp >= %s
          AND order_purchase_timestamp < (%s::date + INTERVAL '1 day')
          AND (%s = 'all' OR customer_state = %s)
    )
    """

    queries = {
        "monthly": source + """
            SELECT
                purchase_month,
                COUNT(*) AS eligible,
                COUNT(*) FILTER (WHERE is_late_calendar) AS late
            FROM base
            GROUP BY purchase_month
            ORDER BY purchase_month
        """,
        "duration": source + """
            SELECT
                CASE
                    WHEN actual_days < 0 THEN 'Negative'
                    WHEN actual_days < 7 THEN '0–6 days'
                    WHEN actual_days < 14 THEN '7–13 days'
                    WHEN actual_days < 21 THEN '14–20 days'
                    WHEN actual_days < 30 THEN '21–29 days'
                    WHEN actual_days < 45 THEN '30–44 days'
                    ELSE '45+ days'
                END AS duration_band,
                COUNT(*) AS orders
            FROM base
            WHERE actual_days IS NOT NULL
            GROUP BY 1
        """,
        "comparison": source + """
            SELECT
                FLOOR(promised_days / 5)::integer * 5 AS promised_bin,
                FLOOR(actual_days / 5)::integer * 5 AS actual_bin,
                COUNT(*) AS orders
            FROM base
            WHERE promised_days >= 0
              AND actual_days >= 0
              AND promised_days IS NOT NULL
              AND actual_days IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1, 2
        """,
        "quality": source + """
            SELECT
                COUNT(*) AS eligible,
                COUNT(*) FILTER (WHERE actual_days IS NULL) AS missing_actual,
                COUNT(*) FILTER (WHERE actual_days < 0) AS negative_actual,
                COUNT(*) FILTER (WHERE promised_days < 0) AS negative_promised
            FROM base
        """
    }

    arguments = (start, end, state, state)
    result = {}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for name, query in queries.items():
                cursor.execute(query, arguments)
                result[name] = cursor.fetchall()

    quality = result["quality"][0]

    return {
        "monthly": [
            {
                "month": row[0].isoformat(),
                "eligible": int(row[1]),
                "late": int(row[2])
            }
            for row in result["monthly"]
        ],
        "duration": [
            {"band": str(row[0]), "orders": int(row[1])}
            for row in result["duration"]
        ],
        "comparison": [
            {
                "promised_bin": int(row[0]),
                "actual_bin": int(row[1]),
                "orders": int(row[2])
            }
            for row in result["comparison"]
        ],
        "quality": {
            "eligible": int(quality[0]),
            "missing_actual": int(quality[1]),
            "negative_actual": int(quality[2]),
            "negative_promised": int(quality[3])
        }
    }

def operations_additional_data(start_date, end_date, state="all"):
    from datetime import date

    start = date.fromisoformat(str(start_date)[:10])
    end = date.fromisoformat(str(end_date)[:10])

    if start > end:
        raise ValueError("Invalid date interval")

    if state != "all" and state not in operations_states():
        raise ValueError("Invalid customer state")

    order_base = """
    WITH base AS (
        SELECT
            order_id,
            customer_state,
            DATE_TRUNC('month', order_purchase_timestamp)::date AS purchase_month,
            gross_item_value,
            freight_value,
            delivery_sla_eligible,
            is_late_calendar,
            average_review_score
        FROM analytics.v_order_intelligence
        WHERE order_purchase_timestamp >= %s
          AND order_purchase_timestamp < (%s::date + INTERVAL '1 day')
          AND (%s = 'all' OR customer_state = %s)
    )
    """

    queries = {
        "geography": order_base + """
            SELECT
                customer_state,
                COUNT(*) FILTER (WHERE delivery_sla_eligible) AS eligible,
                COUNT(*) FILTER (
                    WHERE delivery_sla_eligible AND is_late_calendar
                ) AS late,
                COALESCE(SUM(gross_item_value) FILTER (
                    WHERE delivery_sla_eligible
                ), 0) AS item_value,
                COALESCE(SUM(freight_value) FILTER (
                    WHERE delivery_sla_eligible
                ), 0) AS freight_value
            FROM base
            GROUP BY customer_state
            ORDER BY eligible DESC, customer_state
        """,
        "monthly": order_base + """
            SELECT
                purchase_month,
                COUNT(*) FILTER (
                    WHERE delivery_sla_eligible AND NOT is_late_calendar
                ) AS on_time,
                COUNT(*) FILTER (
                    WHERE delivery_sla_eligible AND is_late_calendar
                ) AS late
            FROM base
            GROUP BY purchase_month
            ORDER BY purchase_month
        """,
        "freight": order_base + """
            SELECT
                CASE
                    WHEN freight_value IS NULL THEN 'Missing'
                    WHEN freight_value < 10 THEN 'Below R$10'
                    WHEN freight_value < 20 THEN 'R$10–19'
                    WHEN freight_value < 40 THEN 'R$20–39'
                    WHEN freight_value < 80 THEN 'R$40–79'
                    ELSE 'R$80+'
                END AS freight_band,
                COUNT(*) AS orders
            FROM base
            WHERE delivery_sla_eligible
            GROUP BY 1
        """,
        "reviews": order_base + """
            SELECT
                is_late_calendar,
                ROUND(average_review_score)::integer AS review_score,
                COUNT(*) AS orders
            FROM base
            WHERE delivery_sla_eligible
              AND average_review_score IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1, 2
        """,
        "sellers": order_base + """
            SELECT
                s.seller_id,
                COUNT(*) AS seller_order_pairs,
                COUNT(*) FILTER (WHERE b.delivery_sla_eligible) AS eligible,
                COUNT(*) FILTER (
                    WHERE b.delivery_sla_eligible AND b.is_late_calendar
                ) AS late
            FROM base b
            INNER JOIN analytics.v_seller_intelligence s
                ON s.order_id = b.order_id
            GROUP BY s.seller_id
        """
    }

    params = (start, end, state, state)
    result = {}

    with get_connection() as connection:
        with connection.cursor() as cursor:
            for name, query in queries.items():
                cursor.execute(query, params)
                result[name] = cursor.fetchall()

    return {
        "geography": [
            {
                "state": str(r[0]) if r[0] is not None else "Unknown",
                "eligible": int(r[1]),
                "late": int(r[2]),
                "item_value": float(r[3]),
                "freight_value": float(r[4])
            }
            for r in result["geography"]
        ],
        "monthly": [
            {
                "month": r[0].isoformat(),
                "on_time": int(r[1]),
                "late": int(r[2])
            }
            for r in result["monthly"]
        ],
        "freight": [
            {"band": str(r[0]), "orders": int(r[1])}
            for r in result["freight"]
        ],
        "reviews": [
            {
                "late": bool(r[0]),
                "score": int(r[1]),
                "orders": int(r[2])
            }
            for r in result["reviews"]
        ],
        "sellers": [
            {
                "seller_id": str(r[0]),
                "seller_orders": int(r[1]),
                "eligible": int(r[2]),
                "late": int(r[3])
            }
            for r in result["sellers"]
        ]
    }
