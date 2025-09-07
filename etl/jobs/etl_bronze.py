from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, to_timestamp, to_json, col
import os

# Path to MySQL JDBC jar
JDBC_JAR = "/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"

# -------------------------------------------------------------------
# Build Spark Session once, with JDBC connector on classpath
# -------------------------------------------------------------------
spark = (
    SparkSession.builder
        .appName("bronze-loader")
        .config("spark.jars", JDBC_JAR)
        .config("spark.driver.extraClassPath", JDBC_JAR)
        .config("spark.executor.extraClassPath", JDBC_JAR)
        .getOrCreate()
)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------
def jdbc_props():
    """Common JDBC connection properties."""
    return {
        "user": os.environ["MYSQL_USER"],
        "password": os.environ["MYSQL_PASSWORD"],
        "driver": "com.mysql.cj.jdbc.Driver"
    }

def mysql_url(db: str) -> str:
    """Build JDBC URL for given DB schema."""
    host = os.environ["MYSQL_HOST"]
    port = os.environ["MYSQL_PORT"]
    return f"jdbc:mysql://{host}:{port}/{db}?useSSL=false&rewriteBatchedStatements=true"

def load_oltp_orders():
    """Read source OLTP orders table."""
    src_url = os.environ["OLTP_JDBC_URL"]
    src_props = {
        "user": os.environ["OLTP_USER"],
        "password": os.environ["OLTP_PASSWORD"],
        "driver": "com.mysql.cj.jdbc.Driver"
    }
    return spark.read.jdbc(src_url, "orders", properties=src_props)

def load_clickstream():
    """Read raw clickstream JSON files."""
    path = os.environ.get("CLICKSTREAM_PATH", "/opt/etl/data/clickstream/*.jsonl")
    return spark.read.json(path)

# -------------------------------------------------------------------
# Main ETL (Bronze layer)
# -------------------------------------------------------------------
if __name__ == "__main__":

    # --- Orders from OLTP ---
    df_orders = (
        load_oltp_orders()
        .withColumn("_ingested_at", current_timestamp())
    )
    (df_orders
        .write
        .mode("overwrite")  # TRUNCATE/replace behavior over JDBC
        .jdbc(mysql_url("bronze"), "orders", properties=jdbc_props()))
    print(f"Wrote {df_orders.count()} rows into bronze.orders")

    # --- Clickstream events ---
    df_events = (
        load_clickstream()
          .select(
              "event_id","user_id","session_id","event_type",
              "page","route","element","ts","metadata"
          )
          # parse ISO timestamp like 2025-09-07T09:55:58Z
          .withColumn("ts", to_timestamp(col("ts"), "yyyy-MM-dd'T'HH:mm:ss'Z'"))
          .withColumn("_ingested_at", current_timestamp())
          # serialize metadata struct/map -> JSON string (valid for MySQL JSON)
          .withColumn("metadata_json", to_json(col("metadata")))
          .drop("metadata")
    )

    # APPEND to pre-created table. No createTableColumnTypes option.
    (df_events.write
        .mode("append")
        .jdbc(mysql_url("bronze"), "click_events", properties=jdbc_props()))

    spark.stop()
