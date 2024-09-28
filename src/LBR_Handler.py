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

            # Batch processing for merging nodes
            merge_query = """
            // Step 1: Identify groups of nodes connected by SAME_AS relationships
MATCH (n)-[:SAME_AS*]-(m)
WHERE id(n) < id(m)
WITH n, collect(m) AS toMerge
LIMIT 10 // If you want to limit the number of nodes processed at once

// Step 2: Transfer relationships from toMerge nodes to the main node
UNWIND toMerge AS duplicate
// Transfer outgoing relationships
MATCH (duplicate)-[r]->(target)
MERGE (n)-[newRel:SAME_AS]->(target)
SET newRel = r

// Transfer incoming relationships
WITH n, duplicate
MATCH (source)-[r]->(duplicate)
MERGE (source)-[newRel:SAME_AS]->(n)
SET newRel = r

// Step 3: Delete the duplicate nodes
DETACH DELETE duplicate

RETURN n;
            """

            session.run(merge_query)

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
                    // Connect Appartment nodes with the same name
                    MATCH (a1:Appartment), (a2:Appartment)
                    WHERE a1.name = a2.name AND id(a1) < id(a2)
                   CREATE (a1)-[:SAME_AS]->(a2);

                    // Connect Reinigungsmitarbeiter nodes with the same name
                    MATCH (r1:Reinigungsmitarbeiter), (r2:Reinigungsmitarbeiter)
                    WHERE r1.name = r2.name AND id(r1) < id(r2)
                   CREATE (r1)-[:SAME_AS]->(r2);

                    // Connect Review nodes with the same text
                    MATCH (rev1:review), (rev2:review)
                    WHERE rev1.text = rev2.text AND id(rev1) < id(rev2)
                   CREATE (rev1)-[:SAME_AS]->(rev2);

                    // Connect Emotion nodes with the same text
                    MATCH (em1:emotion), (em2:emotion)
                    WHERE em1.text = em2.text AND id(em1) < id(em2)
                   CREATE (em1)-[:SAME_AS]->(em2);


                    """
            result = session.run(query, startValue=start_value, endValue=end_value)
            # Extract the boolean value from the result
            record = result.single()
            return record["isConnected"] if record else False
        except Exception as e:
         raise Exception("Could not identify if nodes are connected")


if __name__ == '__main__':
    infer_logic_connection()