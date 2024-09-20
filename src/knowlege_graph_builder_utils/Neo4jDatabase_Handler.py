from neo4j import GraphDatabase
import pandas as pd
# Define the connection URI
uri = "bolt://localhost:7687"  # Default port for Bolt protocol

# Define a class to handle Neo4j interactions
class Neo4jDatabase_Handler:
    def __init__(self, uri):
        self.driver = GraphDatabase.driver(uri, auth=None)  # No authentication

    def close(self):
        self.driver.close()

    def populate_data(self,data:pd.DataFrame):
        with self.driver.session() as session:
            session.write_transaction(self._create_data)

    @staticmethod
    def _create_data(tx):
        # Sample data - create nodes and relationships
        tx.run("CREATE (a:Person {name: 'Alice', age: 30})")
        tx.run("CREATE (b:Person {name: 'Bob', age: 25})")
        tx.run("CREATE (c:Person {name: 'Carol', age: 35})")
        tx.run("CREATE (a)-[:FRIENDS_WITH]->(b)")
        tx.run("CREATE (b)-[:FRIENDS_WITH]->(c)")
        tx.run("CREATE (c)-[:FRIENDS_WITH]->(a)")

if __name__ == "__main__":
    # Initialize the Neo4j database handler
    db = Neo4jDatabase(uri)

    try:
        # Populate the database with data
        db.populate_data()
        print("Data successfully populated into the Neo4j database.")
    finally:
        # Ensure the database connection is closed
        db.close()
