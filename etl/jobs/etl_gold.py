# /opt/etl/jobs/etl_gold.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, date_format, countDistinct, to_timestamp, lower, trim,
    to_date, sum as _sum
)
import os

JDBC_JAR = "/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"

spark = (
    SparkSession.builder
    .appName("gold-star")
    .config("spark.jars", JDBC_JAR)
    .config("spark.driver.extraClassPath", JDBC_JAR)
    .config("spark.executor.extraClassPath", JDBC_JAR)
    .getOrCreate()
)

def jdbc_props():
    return {
        "user": os.environ["MYSQL_USER"],
        "password": os.environ["MYSQL_PASSWORD"],
        "driver": "com.mysql.cj.jdbc.Driver",
    }

def mysql_url(db: str) -> str:
    host = os.environ["MYSQL_HOST"]
    port = os.environ["MYSQL_PORT"]
    return f"jdbc:mysql://{host}:{port}/{db}?useSSL=false&rewriteBatchedStatements=true"

if __name__ == "__main__":
    # ------------------------------------------------------------
    # INPUTS
    # ------------------------------------------------------------
    # 1) Clicks from silver (you have this table)
    clicks = spark.read.jdbc(mysql_url("silver"), "click_events", properties=jdbc_props())
    clicks = (clicks
        .withColumn("user_id", col("user_id"))
        .withColumn("session_id", col("session_id"))
        .withColumn("page", col("page_path"))                    # rename for facts
        .withColumn("event_type", lower(trim(col("event_type"))))
        .withColumn("ts_utc", to_timestamp(col("ts_utc")))
    )

    # 2) Orders from bronze (since silver/orders_curated aren’t ready)
    orders = spark.read.jdbc(mysql_url("bronze"), "orders", properties=jdbc_props())
    orders = (orders
        .withColumn("order_id", col("order_id"))
        .withColumn("user_id", col("user_id"))
        .withColumn("status", lower(trim(col("status"))))
        .withColumn("total_amount", col("total_amount"))
        .withColumn("order_ts", to_timestamp(col("created_at")))
    )

    # ------------------------------------------------------------
    # DIMENSIONS
    # ------------------------------------------------------------
    # dim_user from both clicks + orders (union then distinct)
    dim_user_from_clicks = clicks.select("user_id").where(col("user_id").isNotNull())
    dim_user_from_orders = orders.select("user_id").where(col("user_id").isNotNull())
    dim_user_all = dim_user_from_clicks.unionByName(dim_user_from_orders).dropDuplicates()
    dim_user = dim_user_all.withColumn("user_key", col("user_id").cast("string")).select("user_id", "user_key")

    dim_user.write.mode("overwrite").jdbc(mysql_url("gold"), "dim_user", properties=jdbc_props())

    # ------------------------------------------------------------
    # FACTS
    # ------------------------------------------------------------
    # fact_orders (snapshot granularity: order)
    fact_orders = (
        orders
        .withColumn("order_date_key", date_format(col("order_ts"), "yyyyMMdd").cast("int"))
        .withColumn("product_count", (col("total_amount")*0 + 1).cast("int"))  # placeholder
        .select("order_id", "user_id", "product_count", "total_amount", "order_date_key", "status")
    )
    # overwrite to keep idempotent
    fact_orders.write.mode("overwrite").jdbc(mysql_url("gold"), "fact_orders", properties=jdbc_props())

    # fact_clicks (aggregate by session/user/page/event_type/date)
    fact_clicks = (
        clicks
        .withColumn("event_date_key", date_format(col("ts_utc"), "yyyyMMdd").cast("int"))
        .groupBy("session_id", "user_id", "page", "event_type", "event_date_key")
        .agg(countDistinct("event_id").alias("events_count"))
    )
    fact_clicks.write.mode("overwrite").jdbc(mysql_url("gold"), "fact_clicks", properties=jdbc_props())

    # Optional extra marts (handy for BI / quick checks)
    # daily revenue
    orders_daily = (
        orders
        .withColumn("order_date", to_date(col("order_ts")))
        .groupBy("order_date")
        .agg(
            countDistinct("order_id").alias("orders"),
            _sum("total_amount").alias("revenue")
        )
        .orderBy("order_date")
    )
    orders_daily.write.mode("overwrite").jdbc(mysql_url("gold"), "orders_daily_revenue", properties=jdbc_props())

    spark.stop()
