-- CTEs and Subqueries Showcase

-- 1. Top 5 product families per store per year using CTE
WITH yearly_family_sales AS (
    SELECT
        store_nbr,
        family,
        EXTRACT(YEAR FROM date) AS year,
        SUM(sales) AS total_sales
    FROM raw.sales
    GROUP BY store_nbr, family, EXTRACT(YEAR FROM date)
),
ranked_families AS (
    SELECT
        store_nbr,
        family,
        year,
        ROUND(total_sales::NUMERIC, 2) AS total_sales,
        RANK() OVER (
            PARTITION BY store_nbr, year
            ORDER BY total_sales DESC
        ) AS rank
    FROM yearly_family_sales
)
SELECT * FROM ranked_families
WHERE rank <= 5
ORDER BY store_nbr, year, rank;

-- 2. Stores that exceeded their city average sales
SELECT
    s.store_nbr,
    s.city,
    s.state,
    ROUND(SUM(sl.sales)::NUMERIC, 2) AS store_total
FROM raw.sales sl
JOIN raw.stores s ON sl.store_nbr = s.store_nbr
GROUP BY s.store_nbr, s.city, s.state
HAVING SUM(sl.sales) > (
    SELECT AVG(city_sales)
    FROM (
        SELECT
            s2.city,
            SUM(sl2.sales) AS city_sales
        FROM raw.sales sl2
        JOIN raw.stores s2 ON sl2.store_nbr = s2.store_nbr
        GROUP BY s2.city
    ) city_avg
)
ORDER BY store_total DESC;

-- 3. Monthly sales trend with 3-month moving average using CTE
WITH monthly_totals AS (
    SELECT
        DATE_TRUNC('month', date) AS month,
        SUM(sales) AS total_sales
    FROM raw.sales
    GROUP BY DATE_TRUNC('month', date)
)
SELECT
    month,
    ROUND(total_sales::NUMERIC, 2) AS total_sales,
    ROUND(AVG(total_sales) OVER (
        ORDER BY month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    )::NUMERIC, 2) AS moving_avg_3m
FROM monthly_totals
ORDER BY month;

-- 4. Best and worst performing day of week per store
WITH daily_dow AS (
    SELECT
        store_nbr,
        TO_CHAR(date, 'Day') AS day_of_week,
        EXTRACT(DOW FROM date) AS dow_num,
        AVG(sales) AS avg_sales
    FROM raw.sales
    GROUP BY store_nbr, TO_CHAR(date, 'Day'), EXTRACT(DOW FROM date)
)
SELECT
    store_nbr,
    MAX(CASE WHEN avg_sales = max_sales THEN day_of_week END) AS best_day,
    MAX(CASE WHEN avg_sales = min_sales THEN day_of_week END) AS worst_day
FROM daily_dow
JOIN (
    SELECT
        store_nbr,
        MAX(avg_sales) AS max_sales,
        MIN(avg_sales) AS min_sales
    FROM daily_dow
    GROUP BY store_nbr
) minmax USING (store_nbr)
GROUP BY store_nbr
ORDER BY store_nbr;