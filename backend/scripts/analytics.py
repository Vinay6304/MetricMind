import os
import time
import threading

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# SNOWFLAKE CONNECTION
# =========================================================

_connection = None
_connection_lock = threading.Lock()


def get_connection():
    """
    Return a valid Snowflake connection.

    A new connection is created when:
    1. No connection exists.
    2. The existing connection is closed.
    3. The existing Snowflake session has expired.
    """

    global _connection

    with _connection_lock:

        # -------------------------------------------------
        # Create a new connection if none exists
        # -------------------------------------------------

        if _connection is None:

            start = time.perf_counter()

            _connection = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA"),
                role=os.getenv("SNOWFLAKE_ROLE")
            )

            print(
                f"New Snowflake connection: "
                f"{time.perf_counter() - start:.2f}s"
            )

        # -------------------------------------------------
        # Reconnect if connection is closed or expired
        # -------------------------------------------------

        elif _connection.is_closed() or _connection.expired:

            try:
                _connection.close()
            except Exception:
                pass

            start = time.perf_counter()

            _connection = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
                database=os.getenv("SNOWFLAKE_DATABASE"),
                schema=os.getenv("SNOWFLAKE_SCHEMA"),
                role=os.getenv("SNOWFLAKE_ROLE")
            )

            print(
                f"Reconnected to Snowflake: "
                f"{time.perf_counter() - start:.2f}s"
            )

        return _connection

# =========================================================
# OVERALL METRICS
# =========================================================

def get_overall_metrics(cursor, region=None):

    query = """
        SELECT
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT,
            ROUND(
                (SUM(REVENUE - COST) / NULLIF(SUM(REVENUE), 0)) * 100,
                2
            ) AS PROFIT_MARGIN_PERCENT
        FROM SALES
    """

    params = ()

    if region:
        query += """
            WHERE REGION = %s
        """
        params = (region,)

    cursor.execute(query, params)

    return cursor.fetchone()


# =========================================================
# REGION METRICS
# =========================================================

def get_region_metrics(cursor, region=None):

    query = """
        SELECT
            REGION,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
    """

    params = ()

    if region:
        query += """ WHERE REGION = %s """
        params = (region,)

    query += """
        GROUP BY REGION
        ORDER BY TOTAL_REVENUE DESC;
    """

    cursor.execute(query, params)

    return cursor.fetchall()


# =========================================================
# PRODUCT METRICS
# =========================================================

def get_product_metrics(cursor, region=None):

    query = """
        SELECT
            PRODUCT,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
    """

    params = ()

    if region:
        query += """
            WHERE REGION = %s
        """
        params = (region,)

    query += """
        GROUP BY PRODUCT
        ORDER BY TOTAL_REVENUE DESC;
    """

    cursor.execute(query, params)

    return cursor.fetchall()

# =========================================================
# MONTHLY METRICS
# =========================================================

def get_monthly_metrics(cursor, region=None):

    query = """
        SELECT
            DATE_TRUNC('MONTH', ORDER_DATE) AS MONTH,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
    """

    params = ()

    if region:
        query += """
            WHERE REGION = %s
        """
        params = (region,)

    query += """
        GROUP BY DATE_TRUNC('MONTH', ORDER_DATE)
        ORDER BY MONTH;
    """

    cursor.execute(query, params)

    return cursor.fetchall()


# =========================================================
# COUNTRY METRICS
# =========================================================

def get_country_metrics(cursor, region=None):

    query = """
        SELECT
            COUNTRY,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
    """

    params = ()

    if region:
        query += """
            WHERE REGION = %s
        """
        params = (region,)

    query += """
        GROUP BY COUNTRY
        ORDER BY TOTAL_REVENUE DESC;
    """

    cursor.execute(query, params)

    return cursor.fetchall()


# =========================================================
# DASHBOARD DATA
# =========================================================

def get_dashboard_data(region=None):

    total_start = time.perf_counter()

    conn = get_connection()

    cursor = None

    try:

        cursor = conn.cursor()

        # -------------------------------------------------
        # OVERALL
        # -------------------------------------------------

        start = time.perf_counter()

        overall = get_overall_metrics(cursor, region)

        print(
            f"Overall: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # REGIONS
        # -------------------------------------------------

        start = time.perf_counter()

        regions = get_region_metrics(cursor, region)

        print(
            f"Regions: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # PRODUCTS
        # -------------------------------------------------

        start = time.perf_counter()

        products = get_product_metrics(cursor, region)

        print(
            f"Products: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # MONTHS
        # -------------------------------------------------

        start = time.perf_counter()

        months = get_monthly_metrics(cursor, region)

        print(
            f"Months: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # COUNTRIES
        # -------------------------------------------------

        start = time.perf_counter()

        countries = get_country_metrics(cursor, region)

        print(
            f"Countries: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # RETURN DATA
        # -------------------------------------------------

        dashboard_data = {
            "overall": overall,
            "regions": regions,
            "products": products,
            "months": months,
            "countries": countries
        }

        print(
            f"Total dashboard data time: "
            f"{time.perf_counter() - total_start:.2f}s"
        )

        return dashboard_data

    finally:

        # IMPORTANT:
        # Close ONLY the cursor.
        # Do NOT close the Snowflake connection.
        # The connection will be reused.

        if cursor is not None:
            cursor.close()


 # =========================================================
# CUBE API
# =========================================================

import requests
import json

def get_cube_dashboard_data():

    cube_url = "http://localhost:4000/cubejs-api/v1/load"

    query = {
        "measures": [
            "sales.count",
            "sales.revenue",
            "sales.cost",
            "sales.profit"
        ]
    }

    response = requests.get(
        cube_url,
        params={"query": json.dumps(query)}
    )

    response.raise_for_status()

    return response.json()