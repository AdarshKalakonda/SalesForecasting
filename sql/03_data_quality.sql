-- Data Quality Checks for raw.sales

-- Check 1: NULL values in critical columns
SELECT 
    'NULL Check' AS check_name,
    COUNT(*) FILTER (WHERE date IS NULL)        AS null_dates,
    COUNT(*) FILTER (WHERE store_nbr IS NULL)   AS null_store,
    COUNT(*) FILTER (WHERE family IS NULL)      AS null_family,
    COUNT(*) FILTER (WHERE sales IS NULL)       AS null_sales
FROM raw.sales;

-- Check 2: Negative sales values
SELECT 
    'Negative Sales' AS check_name,
    COUNT(*) AS negative_count
FROM raw.sales
WHERE sales < 0;

-- Check 3: Duplicate records
SELECT 
    'Duplicates' AS check_name,
    COUNT(*) AS duplicate_count
FROM (
    SELECT date, store_nbr, family, COUNT(*) AS cnt
    FROM raw.sales
    GROUP BY date, store_nbr, family
    HAVING COUNT(*) > 1
) duplicates;

-- Check 4: Date range validation
SELECT 
    'Date Range' AS check_name,
    MIN(date) AS earliest_date,
    MAX(date) AS latest_date,
    COUNT(DISTINCT date) AS total_days
FROM raw.sales;

-- Check 5: Orphaned store numbers
SELECT 
    'Orphaned Stores' AS check_name,
    COUNT(*) AS orphaned_count
FROM raw.sales s
LEFT JOIN raw.stores st ON s.store_nbr = st.store_nbr
WHERE st.store_nbr IS NULL;