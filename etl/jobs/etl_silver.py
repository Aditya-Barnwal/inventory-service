from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, trim, current_timestamp, coalesce, to_timestamp, lit, row_number
from pyspark.sql.window import Window
import os

JDBC_JAR = "/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"

spark = (
    SparkSession.builder
        .appName("silver-orders")
        .config("spark.jars", JDBC_JAR)
        .config("spark.driver.extraClassPath", JDBC_JAR)
        .config("spark.executor.extraClassPath", JDBC_JAR)
        .getOrCreate()
)

def jdbc_props():
    return {
        "user": os.environ["MYSQL_USER"],
        "password": os.environ["MYSQL_PASSWORD"],
        "driver": "com.mysql.cj.jdbc.Driver"
    }

def mysql_url(db: str) -> str:
    return f"jdbc:mysql://{os.environ[MYSQL_HOST]}:{os.environ[MYSQL_PORT]}/{db}?useSSL=false&rewriteBatchedStatements=true"

bz = spark.read.jdbc(mysql_url("bronze"), "orders", properties=jdbc_props())
cols = set(bz.columns)
def safe(colname, default=None):
    return col(colname) if colname in cols else lit(default)

df = (
    bz
      .withColumn("order_id",    safe("order_id"))
      .withColumn("customer_id", safe("customer_id"))
      .withColumn("status",      lower(trim(safe("status"))))
      .withColumn("amount",      safe("amount"))
      .withColumn("currency",    safe("currency"))
      .withColumn("order_ts_utc",
                  coalesce(
                      to_timestamp(safe("order_date")),
                      safe("order_ts"),
                      safe("created_at"),
                      safe("updated_at")
                  ))
      .withColumn("_ingested_at", safe("_ingested_at"))
      .withColumn("_processed_at", current_timestamp())
)

w = Window.partitionBy("order_id").orderBy(col("order_ts_utc").desc_nulls_last(), col("_ingested_at").desc_nulls_last())
silver = df.withColumn("rn", row_number().over(w)).where(col("rn")==1).drop("rn")

(
  silver
    .select("order_id","customer_id","status","amount","currency","order_ts_utc","_ingested_at","_processed_at")
    .write
    .mode("overwrite")   # to staging
    .jdbc(mysql_url("silver"), "_orders_stage", properties=jdbc_props())
)

print(f"Prepared {silver.count()} rows for upsert (orders staging).")
spark.stop()
