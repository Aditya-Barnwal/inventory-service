set -euo pipefail

# ---------------------------------------
# Config
# ---------------------------------------
NET=etl_default
MYSQL_HOST=medallion-db
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASS=root
SPARK_CONT=spark-etl

WITH_ORDERS=false
if [[ "${1:-}" == "--with-orders" ]]; then
  WITH_ORDERS=true
fi

mysql_exec () {
  docker run --rm --network "$NET" -i mysql:8 sh -lc \
    "mysql -h${MYSQL_HOST} -P${MYSQL_PORT} -u${MYSQL_USER} -p${MYSQL_PASS} -e \"$1\""
}

echo "==> Ensuring databases exist (silver, gold)"
mysql_exec 'CREATE DATABASE IF NOT EXISTS silver; CREATE DATABASE IF NOT EXISTS gold;'

echo "==> Ensuring silver.orders target table exists (safe if already present)"
mysql_exec "
CREATE TABLE IF NOT EXISTS silver.orders (
  order_id       BIGINT PRIMARY KEY,
  customer_id    BIGINT        NULL,
  status         VARCHAR(64)   NULL,
  amount         DECIMAL(18,2) NULL,
  currency       CHAR(3)       NULL,
  order_ts_utc   DATETIME      NULL,
  _ingested_at   DATETIME      NULL,
  _processed_at  DATETIME      NULL,
  KEY idx_orders_ts (order_ts_utc),
  KEY idx_orders_customer (customer_id)
);"

# ---------------------------------------
# (Optional) SILVER ORDERS (staging -> upsert)
# ---------------------------------------
if $WITH_ORDERS; then
  echo "==> Drop stage so Spark can recreate it cleanly"
  mysql_exec 'DROP TABLE IF EXISTS silver._orders_stage;'

  echo "==> Run Spark orders staging: /opt/etl/jobs/etl_silver_orders.py"
  if docker exec -it "$SPARK_CONT" bash -lc 'test -f /opt/etl/jobs/etl_silver_orders.py'; then
    docker exec -it "$SPARK_CONT" bash -lc 'spark-submit /opt/etl/jobs/etl_silver_orders.py'
  else
    echo "!! WARNING: /opt/etl/jobs/etl_silver_orders.py not found; skipping orders refresh."
  fi

  echo "==> Check staged rows"
  mysql_exec 'SELECT COUNT(*) AS staged_orders FROM silver._orders_stage;'

  echo "==> Upsert silver._orders_stage -> silver.orders"
  mysql_exec '
INSERT INTO silver.orders (
  order_id, customer_id, status, amount, currency, order_ts_utc, _ingested_at, _processed_at
)
SELECT s.order_id, s.customer_id, s.status, s.amount, s.currency, s.order_ts_utc, s._ingested_at, s._processed_at
FROM silver._orders_stage s
ON DUPLICATE KEY UPDATE
  customer_id   = VALUES(customer_id),
  status        = VALUES(status),
  amount        = VALUES(amount),
  currency      = VALUES(currency),
  order_ts_utc  = VALUES(order_ts_utc),
  _ingested_at  = VALUES(_ingested_at),
  _processed_at = VALUES(_processed_at);
'

  echo "==> silver.orders row count after upsert"
  mysql_exec 'SELECT COUNT(*) AS silver_orders_after_upsert FROM silver.orders;'
fi

# ---------------------------------------
# SILVER CLICKS (staging -> upsert)
# ---------------------------------------
echo "==> Refresh silver clicks staging"
docker exec -it "$SPARK_CONT" bash -lc 'spark-submit /opt/etl/jobs/etl_silver_clicks_upsert.py'

echo "==> Upsert silver._click_events_stage -> silver.click_events"
mysql_exec '
INSERT INTO silver.click_events (
  event_id, user_id, session_id, event_type, page_path, route_path, element,
  ts_utc, browser, os, device, country, campaign, metadata_json, _ingested_at, _processed_at
)
SELECT
  s.event_id, s.user_id, s.session_id, s.event_type, s.page_path, s.route_path, s.element,
  s.ts_utc, s.browser, s.os, s.device, s.country, s.campaign, s.metadata_json, s._ingested_at, s._processed_at
FROM silver._click_events_stage s
ON DUPLICATE KEY UPDATE
  user_id       = VALUES(user_id),
  session_id    = VALUES(session_id),
  event_type    = VALUES(event_type),
  page_path     = VALUES(page_path),
  route_path    = VALUES(route_path),
  element       = VALUES(element),
  ts_utc        = VALUES(ts_utc),
  browser       = VALUES(browser),
  os            = VALUES(os),
  device        = VALUES(device),
  country       = VALUES(country),
  campaign      = VALUES(campaign),
  metadata_json = VALUES(metadata_json),
  _ingested_at  = VALUES(_ingested_at),
  _processed_at = VALUES(_processed_at);
TRUNCATE TABLE silver._click_events_stage;
'

# ---------------------------------------
# GOLD (facts + dims)
# ---------------------------------------
echo "==> Run gold job"
docker exec -it "$SPARK_CONT" bash -lc 'spark-submit /opt/etl/jobs/etl_gold.py'

# ---------------------------------------
# Verification
# ---------------------------------------
echo "==> Verification"
if $WITH_ORDERS; then
  ORDERS_SQL="SELECT COUNT(*) AS silver_orders FROM silver.orders;"
else
  ORDERS_SQL="SELECT 'skipped (--with-orders not set)' AS silver_orders;"
fi

mysql_exec "
SHOW TABLES IN gold;
SELECT COUNT(*) AS silver_clicks FROM silver.click_events;
${ORDERS_SQL}
SELECT COUNT(*) AS fact_orders FROM gold.fact_orders;
SELECT COUNT(*) AS fact_clicks FROM gold.fact_clicks;
SELECT * FROM gold.orders_daily_revenue ORDER BY order_date;
"

echo '==> Done.'
