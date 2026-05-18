-- Window Functions Showcase

-- 1. 7-day and 30-day rolling average sales per store per family
SELECT
    date,
    store_nbr,
    family,
    sales,
    ROUND(AVG(sales) OVER (
        PARTITION BY store_nbr, family
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )::NUMERIC, 4) AS rolling_7d_avg,
    ROUND(AVG(sales) OVER (
        PARTITION BY store_nbr, family
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    )::NUMERIC, 4) AS rolling_30d_avg
FROM raw.sales
ORDER BY store_nbr, family, date
LIMIT 100;

-- 2. Overall store revenue rank
SELECT
    store_nbr,
    ROUND(SUM(sales)::NUMERIC, 2) AS total_revenue,
    RANK() OVER (ORDER BY SUM(sales) DESC) AS revenue_rank
FROM raw.sales
GROUP BY store_nbr
ORDER BY revenue_rank;

-- 3. Month over month growth per store
WITH monthly AS (
    SELECT
        store_nbr,
        DATE_TRUNC('month', date) AS month,
        SUM(sales) AS monthly_sales
    FROM raw.sales
    GROUP BY store_nbr, DATE_TRUNC('month', date)
)
SELECT
    store_nbr,
    month,
    ROUND(monthly_sales::NUMERIC, 2) AS monthly_sales,
    ROUND(LAG(monthly_sales) OVER (
        PARTITION BY store_nbr ORDER BY month
    )::NUMERIC, 2) AS prev_month_sales,
    ROUND((
        (monthly_sales - LAG(monthly_sales) OVER (
            PARTITION BY store_nbr ORDER BY month
        )) / NULLIF(LAG(monthly_sales) OVER (
            PARTITION BY store_nbr ORDER BY month
        ), 0) * 100
    )::NUMERIC, 2) AS mom_growth_pct
FROM monthly
ORDER BY store_nbr, month;

-- 4. Running total sales per store
SELECT
    date,
    store_nbr,
    sales,
    ROUND(SUM(sales) OVER (
        PARTITION BY store_nbr
        ORDER BY date
    )::NUMERIC, 2) AS running_total
FROM raw.sales
ORDER BY store_nbr, date
LIMIT 100;

-- 5. Top 3 product families per store by total sales
SELECT *
FROM (
    SELECT
        store_nbr,
        family,
        ROUND(SUM(sales)::NUMERIC, 2) AS total_sales,
        RANK() OVER (
            PARTITION BY store_nbr
            ORDER BY SUM(sales) DESC
        ) AS family_rank
    FROM raw.sales
    GROUP BY store_nbr, family
) ranked
WHERE family_rank <= 3
ORDER BY store_nbr, family_rank;