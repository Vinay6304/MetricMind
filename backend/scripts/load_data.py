import os
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

# Read CSV
df = pd.read_csv("data/raw/sales.csv")

print(f"CSV loaded successfully: {len(df)} rows")

# Connect to Snowflake
conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema=os.getenv("SNOWFLAKE_SCHEMA"),
    role=os.getenv("SNOWFLAKE_ROLE")
)

print("Connected to Snowflake!")

# Insert rows
cursor = conn.cursor()

insert_sql = """
    INSERT INTO SALES
    (ORDER_ID, ORDER_DATE, REGION, COUNTRY, PRODUCT, REVENUE, COST)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

for _, row in df.iterrows():
    cursor.execute(
        insert_sql,
        (
            row["order_id"],
            row["order_date"],
            row["region"],
            row["country"],
            row["product"],
            row["revenue"],
            row["cost"]
        )
    )

conn.commit()

print(f"Successfully inserted {len(df)} rows into SALES!")

cursor.close()
conn.close()

print("Connection closed.")