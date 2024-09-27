from neo4j import GraphDatabase
import pandas as pd


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def write_to_neo4j(self, df):
        with self.driver.session() as session:
            for index, row in df.iterrows():
                session.write_transaction(self._create_and_connect_nodes, row)

    @staticmethod
    def _create_and_connect_nodes(tx, row):
        query = """
        MERGE (b:Booking {Booking_ID: $Booking_ID})
        MERGE (s:StartDate {Date: $Start_date_of_stay})
        MERGE (a:Appartement {Name: $Appartement})
        MERGE (c:Cleaner {Name: $Cleaner})
        MERGE (r:Review {Text: $Review_Text})
        MERGE (se:Sentiment {Scores: $Sentiment_Scores})
        MERGE (ie:IssueEntities {Entities: $Issue_Entities})
        MERGE (ia:Adjectives {Adjectives: $Issue_Entities_Adjectives})

        MERGE (b)-[:HAS_START_DATE]->(s)
        MERGE (b)-[:HAS_APPARTEMENT]->(a)
        MERGE (b)-[:HAS_CLEANER]->(c)
        MERGE (b)-[:HAS_REVIEW]->(r)
        MERGE (r)-[:HAS_SENTIMENT]->(se)
        MERGE (r)-[:HAS_ISSUE_ENTITIES]->(ie)
        MERGE (ie)-[:DESCRIBED_BY]->(ia)
        """

        tx.run(query,
               Booking_ID=row['Booking_ID'],
               Start_date_of_stay=row['Start_date_of_stay'],
               Appartement=row['Appartement'],
               Cleaner=row['Cleaner'],
               Review_Text=row['Review Text'],
               Sentiment_Scores=row['Sentiment Scores'],
               Issue_Entities=row['Issue_Entities'],
               Issue_Entities_Adjectives=row['Issue_Entities_Adjectives'])


# Example usage with a sample DataFrame
data = {
    'Booking_ID': [1],
    'Start_date_of_stay': ['2024-09-27'],
    'Appartement': ['Sea View'],
    'Cleaner': ['John Doe'],
    'Review Text': ['Great stay!'],
    'Sentiment Scores': ['Positive'],
    'Issue_Entities': ['None'],
    'Issue_Entities_Adjectives': ['N/A']
}

df = pd.DataFrame(data)

# Initialize the handler and write data to Neo4j
neo4j_handler = Neo4jHandler("bolt://localhost:7687", "neo4j", "password")
neo4j_handler.write_to_neo4j(df)
neo4j_handler.close()