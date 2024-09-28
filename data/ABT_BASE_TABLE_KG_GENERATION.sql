CREATE TABLE IF NOT EXISTS ABT_BASE_TABLE_KG_GENERATION AS
WITH RandomizedTableB AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY RANDOM()) AS RandomRow
    FROM bas_emotions_customer_reviews
),
NumberedTableA AS (
    SELECT *,
           ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS RowNum
    FROM abt_cleaning_per_app
)
SELECT a.date                              as start_day_of_stay,
       a.appartment,
       a.reinigungsmitarbeiter,
       a.review_text,
       b.emotion,
       b.score
FROM NumberedTableA a
JOIN RandomizedTableB b ON a.RowNum = b.RandomRow;