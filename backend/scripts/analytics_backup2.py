import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )


def get_overall_metrics():
    conn = get_connection()
    cursor = conn.cursor()

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
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result


def get_region_metrics():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            REGION,
            COUNT(*) AS TOTAL_ORDERS,
            SUM(REVENUE) AS TOTAL_REVENUE,
            SUM(COST) AS TOTAL_COST,
            SUM(REVENUE - COST) AS TOTAL_PROFIT
        FROM SALES
        GROUP BY REGION
        ORDER BY TOTAL_REVENUE DESC;
    """

    cursor.execute(query)
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

def get_product_metrics():
    conn = get_connection()
    cursor = conn.cursor()

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
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

def get_monthly_metrics():
    conn = get_connection()
    cursor = conn.cursor()

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
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

def get_country_metrics():
    conn = get_connection()
    cursor = conn.cursor()

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
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return results

def get_dashboard_data():
    return {
        "overall": get_overall_metrics(),
        "regions": get_region_metrics(),
        "products": get_product_metrics(),
        "months": get_monthly_metrics(),
        "countries": get_country_metrics()
    }

if __name__ == "__main__":
    dashboard_data = get_dashboard_data()

    metrics = dashboard_data["overall"]
    print("Overall Metrics")
    print("----------------")
    print(f"Total Orders: {metrics[0]}")
    print(f"Total Revenue: {metrics[1]}")
    print(f"Total Cost: {metrics[2]}")
    print(f"Total Profit: {metrics[3]}")
    print(f"Profit Margin: {metrics[4]}%")

    print("\nRegional Metrics")
    print("----------------")

    regions = get_region_metrics()

    for region in regions:
        print(
            f"{region[0]} | "
            f"Orders: {region[1]} | "
            f"Revenue: {region[2]} | "
            f"Cost: {region[3]} | "
            f"Profit: {region[4]}"
        )

    print("\nProduct Metrics")
    print("----------------")

    products = get_product_metrics()

    for product in products:
        print(
            f"{product[0]} | "
            f"Orders: {product[1]} | "
            f"Revenue: {product[2]} | "
            f"Cost: {product[3]} | "
            f"Profit: {product[4]}"
        )

    print("\nMonthly Metrics")
    print("----------------")

    monthly = get_monthly_metrics()

    for month in monthly:
        print(
            f"{month[0]} | "
            f"Orders: {month[1]} | "
            f"Revenue: {month[2]} | "
            f"Cost: {month[3]} | "
            f"Profit: {month[4]}"
        )

    print("\nCountry Metrics")
    print("----------------")

    countries = get_country_metrics()

    for country in countries:
        print(
            f"{country[0]} | "
            f"Orders: {country[1]} | "
            f"Revenue: {country[2]} | "
            f"Cost: {country[3]} | "
            f"Profit: {country[4]}"
        )
