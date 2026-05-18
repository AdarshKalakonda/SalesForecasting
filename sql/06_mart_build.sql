-- Build mart.daily_sales
INSERT INTO mart.daily_sales (
    date, store_nbr, family, total_sales,
    rolling_7d_avg, rolling_30d_avg, yoy_growth_pct
)
SELECT
    date,
    store_nbr,
    family,
    sales AS total_sales,
    ROUND(AVG(sales) OVER (
        PARTITION BY store_nbr, family
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    )::NUMERIC, 4) AS rolling_7d_avg,
    ROUND(AVG(sales) OVER (
        PARTITION BY store_nbr, family
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    )::NUMERIC, 4) AS rolling_30d_avg,
    ROUND((
        (sales - LAG(sales, 365) OVER (
            PARTITION BY store_nbr, family
            ORDER BY date
        )) / NULLIF(LAG(sales, 365) OVER (
            PARTITION BY store_nbr, family
            ORDER BY date
        ), 0) * 100
    )::NUMERIC, 4) AS yoy_growth_pct
FROM raw.sales;

-- Build mart.store_performance
INSERT INTO mart.store_performance (
    store_nbr, city, state, total_revenue,
    rank_in_city, rank_overall
)
SELECT
    s.store_nbr,
    st.city,
    st.state,
    ROUND(SUM(s.sales)::NUMERIC, 4) AS total_revenue,
    RANK() OVER (
        PARTITION BY st.city
        ORDER BY SUM(s.sales) DESC
    ) AS rank_in_city,
    RANK() OVER (
        ORDER BY SUM(s.sales) DESC
    ) AS rank_overall
FROM raw.sales s
JOIN raw.stores st ON s.store_nbr = st.store_nbr
GROUP BY s.store_nbr, st.city, st.state;