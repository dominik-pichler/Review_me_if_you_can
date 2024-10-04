import pandas as pd
from neo4j import GraphDatabase

def load_demo_data():
    return pd.read_csv('/Users/dominikpichler/Documents/Git/Uni/READ_ME_ALL_DAY_LONG/data/demo_data.csv',sep=',')

# Sample data
data = [
    {"booking_id": 154, "start_day_of_stay": "02.07.24", "appartment": "Art412", "reinigungsmitarbeiter": "iHujBQUu",
     "review_text": "I loved it!", "emotion": "happy", "score": "1.0"},
    {"booking_id": 1, "start_day_of_stay": "18.06.24", "appartment": "Office 2", "reinigungsmitarbeiter": "EnmqMQxj",
     "review_text": "Toll!", "emotion": "neutral", "score": 0.6474594473838806},
    # Add other rows similarly...
]

# Create a DataFrame
df = pd.DataFrame(data)
# Connect to Neo4j
uri = "bolt://localhost:7687"
user = "neo4j"
password = "your_password"
driver = GraphDatabase.driver(uri, auth=(user, password))


def insert_and_connect_data(tx, row_data):
    # Create nodes and relationships for each element in the row
    query = (
        """
         CREATE (b:Booking {booking_id: $booking_id})
         CREATE (s:StartDayOfStay {value: $start_day_of_stay})
         CREATE (a:Appartment {name: $appartment})
         CREATE (r:Reinigungsmitarbeiter {name: $reinigungsmitarbeiter})
         CREATE (rev:review {text: $review_text})
         CREATE (em:emotion {text: $emotion})
         CREATE (sc:score  {text: $score})
         CREATE (ca:perceived_cleaning_quality {value: $perceived_cleaning_quality})

         CREATE (b)-[:HAS_START_DAY]->(s)
         CREATE (b)-[:HAS_BOOKED_APPARTEMENT]->(a)
         CREATE (b)-[:CLEANED_BY]->(r)
         CREATE (b)-[:HAS_REVIEW]->(rev)
         CREATE (rev)-[:HAS_EMOTION]->(em)
         CREATE (em)-[:HAS_SCORE]->(sc)
         
         CREATE (ca)-[:HAS_PERCEIVED_CLEANING]->(r)

         """
    )
    tx.run(query, **row_data)




df = load_demo_data()
# Insert data into Neo4j
with driver.session() as session:
    for index, row in df.iterrows():
        session.write_transaction(insert_and_connect_data, row.to_dict())

print("Data inserted and connected in Neo4j successfully.")

# Close the driver connection
driver.close()