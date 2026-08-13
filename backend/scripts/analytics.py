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
    Reuse the existing Snowflake connection.

    A new connection is created only when:
    1. There is no existing connection.
    2. The existing connection has been closed.
    """

    global _connection

    with _connection_lock:

        # Create a connection if one doesn't exist
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

        # Reconnect if the previous connection was closed
        elif _connection.is_closed():

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

def get_overall_metrics(cursor):

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
        FROM SALES;
    """

    cursor.execute(query)

    return cursor.fetchone()


# =========================================================
# REGION METRICS
# =========================================================

def get_region_metrics(cursor, region=None):

    if region:
        query = """
            SELECT
                REGION,
                COUNT(*) AS TOTAL_ORDERS,
                SUM(REVENUE) AS TOTAL_REVENUE,
                SUM(COST) AS TOTAL_COST,
                SUM(REVENUE - COST) AS TOTAL_PROFIT
            FROM SALES
        """

        params = {}

        if region:
            query += """ WHERE REGION = %(region)s"""
            params["region"] = region
        query += """
            GROUP BY REGION
            ORDER BY TOTAL_REVENUE DESC
        """

    cursor.execute(query, params)

    return cursor.fetchall()


# =========================================================
# PRODUCT METRICS
# =========================================================

def get_product_metrics(cursor):

    query = """
        SELECT
            PRODUCT,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
        GROUP BY PRODUCT
        ORDER BY TOTAL_REVENUE DESC;
    """

    cursor.execute(query)

    return cursor.fetchall()


# =========================================================
# MONTHLY METRICS
# =========================================================

def get_monthly_metrics(cursor):

    query = """
        SELECT
            DATE_TRUNC('MONTH', ORDER_DATE) AS MONTH,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
        GROUP BY DATE_TRUNC('MONTH', ORDER_DATE)
        ORDER BY MONTH;
    """

    cursor.execute(query)

    return cursor.fetchall()


# =========================================================
# COUNTRY METRICS
# =========================================================

def get_country_metrics(cursor):

    query = """
        SELECT
            COUNTRY,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
        GROUP BY COUNTRY
        ORDER BY TOTAL_REVENUE DESC;
    """

    cursor.execute(query)

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

        overall = get_overall_metrics(cursor)

        print(
            f"Overall: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # REGIONS
        # -------------------------------------------------

        start = time.perf_counter()

        regions = get_region_metrics(cursor,region)

        print(
            f"Regions: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # PRODUCTS
        # -------------------------------------------------

        start = time.perf_counter()

        products = get_product_metrics(cursor)

        print(
            f"Products: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # MONTHS
        # -------------------------------------------------

        start = time.perf_counter()

        months = get_monthly_metrics(cursor)

        print(
            f"Months: "
            f"{time.perf_counter() - start:.2f}s"
        )


        # -------------------------------------------------
        # COUNTRIES
        # -------------------------------------------------

        start = time.perf_counter()

        countries = get_country_metrics(cursor)

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
# TESTING
# =========================================================

if __name__ == "__main__":

    dashboard_data = get_dashboard_data()


    # -----------------------------------------------------
    # OVERALL METRICS
    # -----------------------------------------------------

    metrics = dashboard_data["overall"]

    print("\nOverall Metrics")
    print("----------------")

    print(f"Total Orders: {metrics[0]}")
    print(f"Total Revenue: {metrics[1]}")
    print(f"Total Cost: {metrics[2]}")
    print(f"Total Profit: {metrics[3]}")
    print(f"Profit Margin: {metrics[4]}%")


    # -----------------------------------------------------
    # REGIONAL METRICS
    # -----------------------------------------------------

    print("\nRegional Metrics")
    print("----------------")

    for region in dashboard_data["regions"]:

        print(
            f"{region[0]} | "
            f"Orders: {region[1]} | "
            f"Revenue: {region[2]} | "
            f"Cost: {region[3]} | "
            f"Profit: {region[4]}"
        )


    # -----------------------------------------------------
    # PRODUCT METRICS
    # -----------------------------------------------------

    print("\nProduct Metrics")
    print("----------------")

    for product in dashboard_data["products"]:

        print(
            f"{product[0]} | "
            f"Orders: {product[1]} | "
            f"Revenue: {product[2]} | "
            f"Cost: {product[3]} | "
            f"Profit: {product[4]}"
        )


    # -----------------------------------------------------
    # MONTHLY METRICS
    # -----------------------------------------------------

    print("\nMonthly Metrics")
    print("----------------")

    for month in dashboard_data["months"]:

        print(
            f"{month[0]} | "
            f"Orders: {month[1]} | "
            f"Revenue: {month[2]} | "
            f"Cost: {month[3]} | "
            f"Profit: {month[4]}"
        )


    # -----------------------------------------------------
    # COUNTRY METRICS
    # -----------------------------------------------------

    print("\nCountry Metrics")
    print("----------------")

    for country in dashboard_data["countries"]:

        print(
            f"{country[0]} | "
            f"Orders: {country[1]} | "
            f"Revenue: {country[2]} | "
            f"Cost: {country[3]} | "
            f"Profit: {country[4]}"
        )

 # =========================================================
# CUBE API
# =========================================================

import requests


def get_cube_dashboard_data():

    cube_url = "http://localhost:4000/cubejs-api/v1/load"

    query = {
        "measures": [
            "Orders.total_orders",
            "Orders.total_revenue",
            "Orders.total_cost",
            "Orders.total_profit"
        ]
    }

    response = requests.get(
        cube_url,
        params={"query": str(query)}
    )

    response.raise_for_status()

    return response.json()