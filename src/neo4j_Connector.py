from neo4j import GraphDatabase
import pandas as pd

# Define your Neo4j connection details
uri = "bolt://localhost:7687"  # Update with your Neo4j URI
username = "neo4j"  # Update with your username
password = "password"  # Update with your password

# Establish a connection to the Neo4j database
driver = GraphDatabase.driver(uri, auth=(username, password))


def fetch_graph_data():
    with driver.session() as session:
        # Define your Cypher query to fetch nodes and relationships
        query = """
        MATCH (n)-[r]->(m)
        RETURN n.id AS source, m.id AS target, r.weight AS weight
        """
        result = session.run(query)

        # Convert the result to a pandas DataFrame
        data = pd.DataFrame([dict(record) for record in result])

        return data


# Fetch the graph data
graph_data = fetch_graph_data()

# Close the driver connection when done
driver.close()

# Display the fetched data
print(graph_data)