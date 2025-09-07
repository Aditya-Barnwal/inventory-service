-- ===== Databases (schemas) =====
CREATE DATABASE IF NOT EXISTS bronze CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS silver  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS gold    CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

-- ===== BRONZE (raw, append-only) =====
USE bronze;

CREATE TABLE IF NOT EXISTS orders (
  order_id      BIGINT PRIMARY KEY,
  user_id       BIGINT,
  status        VARCHAR(32),
  total_amount  DECIMAL(12,2),
  created_at    DATETIME NULL,
  updated_at    DATETIME NULL,
  _ingested_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS click_events (
  event_id     VARCHAR(64) PRIMARY KEY,
  user_id      BIGINT NULL,
  session_id   VARCHAR(64) NULL,
  event_type   VARCHAR(64) NULL,
  page         VARCHAR(256) NULL,
  route        VARCHAR(256) NULL,
  element      VARCHAR(256) NULL,
  ts           DATETIME NULL,
  metadata     JSON NULL,
  _ingested_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ce_user (user_id),
  INDEX idx_ce_ts (ts)
) ENGINE=InnoDB;

-- ===== SILVER (clean/conformed) =====
USE silver;

CREATE TABLE IF NOT EXISTS orders_curated (
  order_id     BIGINT PRIMARY KEY,
  user_id      BIGINT,
  status       VARCHAR(32),
  total_amount DECIMAL(12,2),
  order_ts     DATETIME,
  updated_at   DATETIME,
  INDEX idx_oc_user (user_id),
  INDEX idx_oc_ts   (order_ts)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS click_events_curated (
  event_id    VARCHAR(64) PRIMARY KEY,
  user_id     BIGINT NULL,
  session_id  VARCHAR(64) NULL,
  event_type  VARCHAR(64) NULL,
  page        VARCHAR(256) NULL,
  route       VARCHAR(256) NULL,
  element     VARCHAR(256) NULL,
  ts_utc      DATETIME NULL,
  search_term VARCHAR(256) NULL,
  device      VARCHAR(64)  NULL,
  INDEX idx_cc_user (user_id),
  INDEX idx_cc_ts   (ts_utc)
) ENGINE=InnoDB;

-- ===== GOLD (star schema) =====
USE gold;

CREATE TABLE IF NOT EXISTS dim_user (
  user_id   BIGINT PRIMARY KEY,
  user_key  VARCHAR(64),
  email     VARCHAR(256) NULL,
  full_name VARCHAR(256) NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS dim_product (
  product_id   BIGINT PRIMARY KEY,
  product_sku  VARCHAR(64),
  product_name VARCHAR(256),
  category     VARCHAR(128),
  price        DECIMAL(12,2)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fact_orders (
  order_id       BIGINT PRIMARY KEY,
  user_id        BIGINT,
  product_count  INT,
  total_amount   DECIMAL(12,2),
  order_date_key INT,
  status         VARCHAR(32),
  INDEX idx_fo_user (user_id),
  INDEX idx_fo_date (order_date_key)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fact_clicks (
  session_id     VARCHAR(64),
  user_id        BIGINT,
  page           VARCHAR(256),
  event_type     VARCHAR(64),
  events_count   INT,
  event_date_key INT,
  INDEX idx_fc_user (user_id),
  INDEX idx_fc_date (event_date_key)
) ENGINE=InnoDB;
