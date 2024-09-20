from review_process_utils.review_translator import translate_reviews
from review_process_utils.sentiment_analysis_bert import get_topic_stats
from review_process_utils.ER_extractor import extract_nouns, extract_nouns_and_adjectives
import os
from credentials import AH_DB_NAME, AH_HOSTNAME, AH_PASSWORD, AH_PORT, AH_SCHEMA_NAME, AH_USERNAME
import psycopg2
import pandas as pd

class ReviewHandler:
    reviews = None
    translate_reviews = None
    processed_reviews = None

    def __init__(self, local_env=False):
        if local_env:
            # Retrieve database connection parameters from environment variables
            rds_host = os.environ['RDS_HOST']
            db_username = os.environ['DB_USERNAME']
            db_password = os.environ['DB_PASSWORD']
            db_name = os.environ['DB_NAME']
            db_port = os.environ.get('DB_PORT', 5432)  # Default PostgreSQL port is 5432

        else:
            rds_host = AH_HOSTNAME
            db_username = AH_USERNAME
            db_password = AH_PASSWORD
            db_name = AH_DB_NAME
            db_port = AH_PORT

            # Establish a connection to the RDS PostgreSQL database
        try:
            self.conn = psycopg2.connect(
                host=rds_host,
                user=db_username,
                password=db_password,
                dbname=db_name,
                port=db_port
            )

            self.cursor = self.conn.cursor()

        except psycopg2.Error as e:
            print(f"ERROR: Could not connect to PostgreSQL instance. {e}")
            raise ConnectionError
    def _fetch_reviews(self) -> bool:
        try:
            query_fetch_reviews = "SELECT BOOKING_ID,REVIEW FROM ABT_KG_Analysis"
            self.cursor.execute(query_fetch_reviews)

            rows = self.cursor.fetchall()

            # Get column names from the cursor description
            colnames = [desc[0] for desc in self.cursor.description]

            # Close the cursor and connection
            self.cursor.close()
            self.conn.close()

            ReviewHandler.reviews = pd.DataFrame(rows, columns=colnames)

            return True
        except psycopg2.Error as e:
            raise ConnectionError

    def _store_processed_reviews(self):
        try:
            table_name = 'ANALYSIS_CUSTOMER_REVIEWS'
            # Create table if it doesn't exist (you may need to adjust the column types)
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                raw_reviews TEXT,
                translated_reviews TEXT,
                sentiments TEXT,
                nouns_and_entities TEXT
            );
            """
            self.cursor.execute(create_table_query)

            # Insert DataFrame rows into the PostgreSQL table
            for _, row in ReviewHandler.processed_reviews.iterrows():
                try:
                    insert_query = f"""
                    INSERT INTO {table_name} (raw_reviews, translated_reviews, sentiments, nouns_and_entities)
                    VALUES (%s, %s, %s, %s);
                    """
                    self.cursor.execute(insert_query,
                                (row['raw_reviews'],
                                 row['translated_reviews'],
                                 row['sentiments'],
                                row['nouns_and_entities']))

                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f'Failed to store {row} due to {e}')
                    continue
        except Exception as e:
            raise e

    def perform_sentiment_analysis(self):
        return get_topic_stats(ReviewHandler.translate_reviews)

    def translate_reviews(self):
        try:
            return translate_reviews(ReviewHandler.translate_reviews)
        except Exception as e:
            raise e
    def extract_nouns_and_adjectives(self):
        try:
            return extract_nouns_and_adjectives(ReviewHandler.translate_reviews)
        except Exception as e:
            print(f"ERROR: Could not extract nouns and adjectives. {e}")
            raise e
    def process_and_store_reviews(self):
        try:
            dict_reviews = {'raw_reviews': self._fetch_reviews(),
                            'translated_reviews': self.translate_reviews(),
                            'sentiments': self.perform_sentiment_analysis(),
                            'nouns_and_entities': self.extract_nouns_and_adjectives()}

            ReviewHandler.processed_reviews = pd.DataFrame(dict_reviews)
            self._store_processed_reviews()
            return ReviewHandler.processed_reviews
        except Exception as e:
            raise e

