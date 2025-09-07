from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, trim, current_timestamp, coalesce, to_timestamp, lit
import os

JDBC_JAR = "/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"

spark = (
    SparkSession.builder
        .appName("silver-orders-staging")
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
    # ✅ correct quoting on env keys
    return f"jdbc:mysql://{os.environ['MYSQL_HOST']}:{os.environ['MYSQL_PORT']}/{db}?useSSL=false&rewriteBatchedStatements=true"

# ---------- Read bronze.orders ----------
bz = spark.read.jdbc(mysql_url("bronze"), "orders", properties=jdbc_props())

# ---------- Map bronze -> silver staging schema ----------
silver_stage = (
    bz
    .withColumn("order_id",    col("order_id"))
    .withColumn("customer_id", col("user_id"))
    .withColumn("status",      lower(trim(col("status"))))
    .withColumn("amount",      col("total_amount"))
    .withColumn("currency",    lit(None).cast("string"))   # keep NULL for now
    .withColumn("order_ts_utc",
                coalesce(to_timestamp(col("created_at")),
                         to_timestamp(col("updated_at"))))
    .withColumn("_processed_at", current_timestamp())
    .select("order_id","customer_id","status","amount","currency","order_ts_utc","_ingested_at","_processed_at")
)

# ---------- Write to staging ----------
(silver_stage.write
    .mode("overwrite")
    .jdbc(mysql_url("silver"), "_orders_stage", properties=jdbc_props()))

print(f"Prepared {silver_stage.count()} rows for upsert (orders staging).")
spark.stop()
