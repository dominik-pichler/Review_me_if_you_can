from neo4j import GraphDatabase
import pandas as pd

uri = "bolt://localhost:7687"  
username = "neo4j"  
password = "password"  

driver = GraphDatabase.driver(uri, auth=(username, password))


def fetch_graph_data():
    with driver.session() as session:
        query = """
        MATCH (n)-[r]->(m)
        RETURN n.id AS source, m.id AS target, r.weight AS weight
        """
        result = session.run(query)

        data = pd.DataFrame([dict(record) for record in result])

        return data

if __name__ == '__main__':

    # Fetch the graph data
    graph_data = fetch_graph_data()

    # Close the driver connection when done
    driver.close()

    # Display the fetched data
    print(graph_data)