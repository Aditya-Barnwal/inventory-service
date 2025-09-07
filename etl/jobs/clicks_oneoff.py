import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp

JDBC_JAR="/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"
spark=(SparkSession.builder
        .appName("clicks-oneoff")
        .config("spark.jars", JDBC_JAR)
        .config("spark.driver.extraClassPath", JDBC_JAR)
        .config("spark.executor.extraClassPath", JDBC_JAR)
        .getOrCreate())

path=os.environ.get("CLICKSTREAM_PATH","/opt/etl/data/clickstream/*.jsonl")
df=spark.read.json(path)
print("clickstream rows:", df.count())

df = (df
      .select("event_id","user_id","session_id","event_type","page","route","element","ts","metadata")
      .withColumn("_ingested_at", current_timestamp()))

props={"user":os.environ["MYSQL_USER"],
       "password":os.environ["MYSQL_PASSWORD"],
       "driver":"com.mysql.cj.jdbc.Driver"}

url=f"jdbc:mysql://{os.environ['MYSQL_HOST']}:{os.environ['MYSQL_PORT']}/bronze?useSSL=false&rewriteBatchedStatements=true"

df.write.mode("append").jdbc(url, "click_events", properties=props)
print("written to bronze.click_events")
spark.stop()
