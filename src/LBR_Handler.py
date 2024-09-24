from neo4j import GraphDatabase
from credentials import neo_uri,neo_password,neo_username


driver = GraphDatabase.driver(neo_uri, auth=(neo_username, neo_password))


def infer_logic_connection() -> bool:
    with driver.session() as session:
        try:
            query= """
                   MATCH (a), (b)
                   WHERE id(a) < id(b)
                   CREATE (a)-[:CONNECTED_TO]->(b)
                   """
            session.run(query)
            return True
        except Exception as e:
            return False

def identify_n_most_connected_nodes(n) -> list:
    with driver.session() as session:
        try:
            query = f"""
                    MATCH (n)-[r]->(m)
                    WITH n, count(r) AS degree
                    ORDER BY degree DESC
                    LIMIT {n} // Replace 'n' with the desired number of top nodes
                    RETURN {n}, degree
                    """
            session.run(query)
        except Exception as e:
            raise Exception("Could not identify most connected nodes")