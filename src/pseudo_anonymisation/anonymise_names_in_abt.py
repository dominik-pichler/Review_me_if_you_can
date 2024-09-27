import psycopg2
import random
import string
from ..credentials import AH_DB_NAME,AH_HOSTNAME,AH_PASSWORD,AH_USERNAME,AH_PORT

def generate_random_name(length=8):
    """Generate a random name of a given length."""
    return ''.join(random.choices(string.ascii_letters, k=length))

def anonymize_names(table_name, name_column):
    """Anonymize names in a specified column of a PostgreSQL table."""
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
                host=AH_HOSTNAME,
                user=AH_USERNAME,
                password=AH_PASSWORD,
                dbname=AH_DB_NAME,
                port=AH_PORT)

        cursor = connection.cursor()

        # Select all names from the table
        select_query = f"SELECT id, {name_column} FROM {table_name};"
        cursor.execute(select_query)
        rows = cursor.fetchall()

        # Anonymize each name and update the table
        for row in rows:
            original_id = row[0]
            random_name = generate_random_name()
            update_query = f"UPDATE {table_name} SET {name_column} = %s WHERE id = %s;"
            cursor.execute(update_query, (random_name, original_id))

        # Commit the changes
        connection.commit()
        print("Names have been anonymized successfully.")

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)

    finally:
        # Close the database connection
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed.")

            # Establish a connection to the RDS PostgreSQL database

def run_anonymise_names_in_abt():
    table_name = 'ABT_BASE_TABLE_KG_GENERATION'
    name_column = 'reinigungsmitarbeiter'
    anonymize_names( table_name, name_column)



if __name__ == '__main__':
    run_anonymise_names_in_abt()