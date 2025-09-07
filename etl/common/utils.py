import os
from pyspark.sql import SparkSession

MYSQL_JAR = "/usr/local/spark/jars/mysql-connector-j-8.3.0.jar"

def make_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .config("spark.jars", MYSQL_JAR)
        .getOrCreate()
    )

def jdbc_props(user_env="MYSQL_USER", pass_env="MYSQL_PASSWORD"):
    return {
        "user": os.environ[user_env],
        "password": os.environ[pass_env],
        "driver": "com.mysql.cj.jdbc.Driver"
    }

def mysql_url(db: str, host_env="MYSQL_HOST", port_env="MYSQL_PORT") -> str:
    host = os.environ.get(host_env, "medallion-db")
    port = os.environ.get(port_env, "3306")
    return f"jdbc:mysql://{host}:{port}/{db}?useSSL=false&rewriteBatchedStatements=true"
