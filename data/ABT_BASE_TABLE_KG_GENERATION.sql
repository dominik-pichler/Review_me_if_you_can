DROP TABLE IF EXISTS ABT_BASE_TABLE_KG_GENERATION;

CREATE TABLE IF NOT EXISTS ABT_BASE_TABLE_KG_GENERATION AS
SELECT ROW_NUMBER() OVER (ORDER BY date) AS BOOKING_ID,
       date                              as start_day_of_stay,
       appartment,
       reinigungsmitarbeiter,
       review_text

FROM abt_cleaning_per_app
LEFT JOIN TOOD! Hier muss noch eine Reivew Tabelle gebaut und gejoint werden!
