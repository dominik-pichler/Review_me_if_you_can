from neo4j import GraphDatabase, Result
from credentials import neo_uri,neo_password,neo_username
from tqdm import tqdm

driver = GraphDatabase.driver(neo_uri, auth=(neo_username, neo_password))


def infer_logic_connection() -> bool:
    """
    Function to infer the logic connection to Neo4j. Connects nodes with the same name or text.
    :return: True if connections have been inferred successfully, False otherwise.
    :rtype: bool
    """
    try:
        with driver.session() as session:
            # Parameterized query for different node labels and properties
            node_types = [
                {"label": "Appartment", "property": "name"},
                {"label": "Reinigungsmitarbeiter", "property": "name"},
                {"label": "review", "property": "text"},
                {"label": "emotion", "property": "text"}
            ]

            for node_type in tqdm(node_types):
                query = f"""
                MATCH (n1:{node_type['label']}), (n2:{node_type['label']})
                WHERE n1.{node_type['property']} = n2.{node_type['property']} AND id(n1) < id(n2)
                CREATE (n1)-[:SAME_AS]->(n2);
                """
                session.run(query)


        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        return False
def identify_n_most_connected_nodes(n) -> Result:
    '''
    Function to identify the most connected nodes of a graph.
    :param n: Limit of most connected nodes to be returned
    :type n:
    :return:
    :rtype:
    '''
    with driver.session() as session:
        try:
            query = f"""
                    MATCH (n)-[r]->(m)
                    WITH n, count(r) AS degree
                    ORDER BY degree DESC
                    LIMIT {n} 
                    RETURN {n}, degree
                    """
            return session.run(query)
        except Exception as e:
            raise Exception("Could not identify most connected nodes")


def connection_check(driver, start_value, end_value) -> bool:
    '''
    Function to check if a node is connected to another node
    '''
    with driver.session() as session:
        try:
            query = """
                  
                    """
            result = session.run(query, startValue=start_value, endValue=end_value)
            # Extract the boolean value from the result
            record = result.single()
            return record["isConnected"] if record else False
        except Exception as e:
         raise Exception("Could not identify if nodes are connected")


if __name__ == '__main__':
    infer_logic_connection()