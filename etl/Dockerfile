# Jupyter + PySpark base (Spark in local mode)
FROM jupyter/pyspark-notebook:latest

USER root
WORKDIR /opt/etl

# Copy MySQL JDBC driver (download mysql-connector-j-8.x and place under etl/jars)
COPY jars/mysql-connector-j-8.3.0.jar /usr/local/spark/jars/

# Python libs for helper JDBC ops (optional) + timezones
RUN pip install --no-cache-dir mysql-connector-python pytz

# Bring in ETL code
COPY jobs/ ./jobs/
COPY common/ ./common/

# Default: start Jupyter (for dev). In CI we'll override with spark-submit.
EXPOSE 8888
