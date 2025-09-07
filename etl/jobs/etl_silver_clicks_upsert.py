from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, trim, current_timestamp, coalesce, to_timestamp, regexp_replace, get_json_object, row_number
from pyspark.sql.window import Window
import os

JDBC_JAR = "/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"

spark = (
    SparkSession.builder
        .appName("silver-clicks-upsert")
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
    return f"jdbc:mysql://{os.environ['MYSQL_HOST']}:{os.environ['MYSQL_PORT']}/{db}?useSSL=false&rewriteBatchedStatements=true"

# 1) read bronze
bronze = spark.read.jdbc(mysql_url("bronze"), "click_events", properties=jdbc_props())

# 2) normalize + enrich
norm = (
    bronze
      .withColumn("event_type_norm", lower(trim(col("event_type"))))
      .withColumn("page_norm",  regexp_replace(trim(col("page")),  r"//+", "/"))
      .withColumn("route_norm", regexp_replace(trim(col("route")), r"//+", "/"))
      .withColumn("ts_utc", coalesce(to_timestamp(col("ts")), col("ts")))
      .withColumn("browser",  get_json_object(col("metadata_json"), "$.browser"))
      .withColumn("os",       get_json_object(col("metadata_json"), "$.os"))
      .withColumn("device",   get_json_object(col("metadata_json"), "$.device"))
      .withColumn("country",  get_json_object(col("metadata_json"), "$.country"))
      .withColumn("campaign", get_json_object(col("metadata_json"), "$.campaign"))
)

# 3) dedupe by event_id (latest ts/_ingested_at)
w = Window.partitionBy("event_id").orderBy(col("ts_utc").desc_nulls_last(), col("_ingested_at").desc_nulls_last())
silver_df = (
    norm
      .withColumn("rn", row_number().over(w)).where(col("rn")==1).drop("rn")
      .select(
        col("event_id"),
        col("user_id"),
        col("session_id"),
        col("event_type_norm").alias("event_type"),
        col("page_norm").alias("page_path"),
        col("route_norm").alias("route_path"),
        col("element"),
        col("ts_utc"),
        col("browser"),
        col("os"),
        col("device"),
        col("country"),
        col("campaign"),
        col("metadata_json"),
        col("_ingested_at"),
        current_timestamp().alias("_processed_at")
      )
)

# 4) write to STAGING
(silver_df.write
    .mode("overwrite")  # replace staging each run
    .jdbc(mysql_url("silver"), "_click_events_stage", properties=jdbc_props())
)

print(f"Prepared {silver_df.count()} rows for upsert (staging).")
spark.stop()
