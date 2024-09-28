from review_process_utils.review_translator import translate_reviews
from review_process_utils.topic_analysis_bert import get_topic_stats
from review_process_utils.emotion_detector import detect_emotions
from review_process_utils.ER_extractor import extract_nouns, extract_nouns_and_adjectives
import os
from credentials import AH_DB_NAME, AH_HOSTNAME, AH_PASSWORD, AH_PORT, AH_SCHEMA_NAME, AH_USERNAME
import psycopg2
import pandas as pd


import time
import functools

def retry(max_tries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for _ in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Error occurred: {e}. Retrying...")
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


class ReviewHandler:
    reviews = None
    translated_reviews = None
    processed_reviews = None
    emotions_reviews = None

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

        except psycopg2.Error as e:
            print(f"ERROR: Could not connect to PostgreSQL instance. {e}")
            raise ConnectionError

    @retry(max_tries=5, delay=2)
    def _fetch_reviews(self) -> bool:
        try:
            cursor = self.conn.cursor()

            query_fetch_reviews = "SELECT DISTINCT review_text,appartment,date FROM ABT_CLEANING_PER_APP WHERE review_text is not null"
            cursor.execute(query_fetch_reviews)

            rows = cursor.fetchall()

            # Get column names from the cursor description
            colnames = [desc[0] for desc in cursor.description]

            # Close the cursor and connection
            cursor.close()

            ReviewHandler.reviews = pd.DataFrame(rows, columns=colnames)
            return True
        except psycopg2.Error as e:
            raise ConnectionError

    @retry(max_tries=5, delay=2)
    def _store_translated_reviews(self) -> bool:
        cursor = self.conn.cursor()
        try:
            table_name = 'BAS_TRANSLATED_CUSTOMER_REVIEWS'
            # Create table if it doesn't exist (you may need to adjust the column types)
            create_table_query = f"""
            DROP TABLE IF EXISTS {table_name};
            CREATE TABLE IF NOT EXISTS {table_name}(
                APPARTMENT TEXT,
                DATE_OF_BOOKING TEXT,
                REVIEW TEXT,
                TRANSLATED_REVIEW TEXT
            );
            """

            cursor.execute(create_table_query)
            self.conn.commit()
            # Insert DataFrame rows into the PostgreSQL table
            for _, row in self.translated_reviews.iterrows():
                try:
                    insert_query = f"""
                    INSERT INTO {table_name} (APPARTMENT,DATE_OF_BOOKING,REVIEW,TRANSLATED_REVIEW)
                    VALUES (%s, %s, %s, %s);
                    """
                    cursor.execute(insert_query,
                                (row['Appartment'],
                                 row['Date'],
                                 row['Review'],
                                 row['Translated_Review']
                                 ))

                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f'Failed to store due to {e}')
                    continue
            cursor.close()
        except Exception as e:
            cursor.close()
            raise e
    def _store_emotions_of_reviews(self):
        self.emotions_reviews.to_csv("emotions.csv")
        cursor = self.conn.cursor()
        try:
            table_name = 'BAS_EMOTIONS_CUSTOMER_REVIEWS'
            # Create table if it doesn't exist (you may need to adjust the column types)
            create_table_query = f"""
                DROP TABLE IF EXISTS {table_name};
                    CREATE TABLE IF NOT EXISTS {table_name}(
                        REVIEW TEXT NOT NULL,
                        EMOTION TEXT NOT NULL,
                        SCORE FLOAT
                    );
                    """

            cursor.execute(create_table_query)
            self.conn.commit()
            # Insert DataFrame rows into the PostgreSQL table
            for _, row in self.emotions_reviews.iterrows():
                try:
                    insert_query = f"""
                            INSERT INTO {table_name} (REVIEW,EMOTION, SCORE)
                            VALUES (%s, %s, %s);
                            """
                    cursor.execute(insert_query,
                                   (row['Text'],
                                    row['Emotion'],
                                    row['Score']
                                    ))

                    self.conn.commit()
                except Exception as e:
                    self.conn.rollback()
                    print(f'Failed to store due to {e}')
                    continue
            cursor.close()
        except Exception as e:
            cursor.close()
            raise e


    def _store_processed_reviews(self):
        try:
            table_name = 'ANALYSIS_CUSTOMER_REVIEWS'
            # Create table if it doesn't exist (you may need to adjust the column types)
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                appartment TEXT NOT NULL,
                review_date TEXT NOT NULL,
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
                    INSERT INTO {table_name} (appartment,review_date, raw_reviews, translated_reviews, sentiments, nouns_and_entities)
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
        self.emotions_reviews =  detect_emotions(self.translated_reviews)

    def translate_reviews(self):
        try:
            self.translated_reviews = translate_reviews(ReviewHandler.reviews)
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

if __name__ == '__main__':
    reviewhandler = ReviewHandler()
    reviewhandler._fetch_reviews()
    reviewhandler.translate_reviews()
    reviewhandler.translated_reviews.to_csv("translated.csv")
    #reviewhandler.perform_sentiment_analysis()
    #reviewhandler._store_emotions_of_reviews()
    reviewhandler._store_translated_reviews()

    print("done")