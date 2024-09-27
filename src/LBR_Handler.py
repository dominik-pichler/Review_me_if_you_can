from neo4j import GraphDatabase, Result
from credentials import neo_uri,neo_password,neo_username


driver = GraphDatabase.driver(neo_uri, auth=(neo_username, neo_password))


def infer_logic_connection() -> bool:
    '''
    Function to infer the logic connection to Neo4j. Thereby all connections of nodes that share the same name,
    regardless of the distance should be connected.
    :return: True if connections have been inferred successfully, False otherwise.
    :rtype: bool
    '''
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
                    LIMIT {n} // Replace 'n' with the desired number of top nodes
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
                    MATCH (startNode {property: $startValue}), (endNode {property: $endValue})
                    RETURN EXISTS((startNode)-[*]-(endNode)) AS isConnected
                    """
            result = session.run(query, startValue=start_value, endValue=end_value)
            # Extract the boolean value from the result
            record = result.single()
            return record["isConnected"] if record else False
        except Exception as e:
            raise Exception("Could not identify if nodes are connected")