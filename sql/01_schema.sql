-- Create raw tables
CREATE TABLE IF NOT EXISTS raw.sales (
    id          BIGINT,
    date        DATE,
    store_nbr   SMALLINT,
    family      VARCHAR(30),
    sales       NUMERIC(12,4),
    onpromotion BOOLEAN
);

CREATE TABLE IF NOT EXISTS raw.stores (
    store_nbr   SMALLINT,
    city        VARCHAR(50),
    state       VARCHAR(50),
    type        VARCHAR(5),
    cluster     SMALLINT
);

CREATE TABLE IF NOT EXISTS raw.oil (
    date        DATE,
    dcoilwtico  NUMERIC(10,4)
);

CREATE TABLE IF NOT EXISTS raw.holidays (
    date        DATE,
    type        VARCHAR(20),
    locale      VARCHAR(20),
    locale_name VARCHAR(50),
    description VARCHAR(100),
    transferred BOOLEAN
);

-- Create mart tables
CREATE TABLE IF NOT EXISTS mart.daily_sales (
    date             DATE,
    store_nbr        SMALLINT,
    family           VARCHAR(30),
    total_sales      NUMERIC(12,4),
    rolling_7d_avg   NUMERIC(12,4),
    rolling_30d_avg  NUMERIC(12,4),
    yoy_growth_pct   NUMERIC(8,4)
);

CREATE TABLE IF NOT EXISTS mart.store_performance (
    store_nbr       SMALLINT,
    city            VARCHAR(50),
    state           VARCHAR(50),
    total_revenue   NUMERIC(15,4),
    rank_in_city    INT,
    rank_overall    INT
);

CREATE TABLE IF NOT EXISTS mart.forecasts (
    store_nbr       SMALLINT,
    family          VARCHAR(30),
    forecast_date   DATE,
    predicted_sales NUMERIC(12,4),
    lower_ci        NUMERIC(12,4),
    upper_ci        NUMERIC(12,4),
    model_version   VARCHAR(20),
    created_at      TIMESTAMP DEFAULT NOW()
);