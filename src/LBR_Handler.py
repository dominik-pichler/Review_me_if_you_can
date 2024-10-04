from neo4j import GraphDatabase, Result
from credentials import neo_uri,neo_password,neo_username
from tqdm import tqdm
import pandas as pd
driver = GraphDatabase.driver(neo_uri, auth=(neo_username, neo_password))




def identify_best_cleaners():
    try:
        with driver.session() as session:
            query= """
             // Match cleaning personnel and their associated reviews and emotions
                MATCH (r:Reinigungsmitarbeiter)<-[:CLEANED_BY]-(b:Booking)-[:HAS_REVIEW]->(rev:Review)-[:HAS_EMOTION]->(em:Emotion)
                WHERE em.text IN ['joy', 'disgust'] // Filter for relevant emotions
            
                // Aggregate emotion counts and total cleanings
                WITH r, em.text AS emotion, count(em) AS emotionCount, count(DISTINCT b) AS totalCleanings
               ORDER BY r.name
            
                // Calculate joy-to-disgust ratio
                WITH r, 
                     sum(CASE WHEN emotion = 'joy' THEN emotionCount ELSE 0 END) AS joyCount,
                     sum(CASE WHEN emotion = 'disgust' THEN emotionCount ELSE 0 END) AS disgustCount,
                     totalCleanings
            
                WITH r, 
                     joyCount, 
                     disgustCount, 
                     totalCleanings,
                     CASE WHEN disgustCount = 0 THEN joyCount ELSE joyCount * 1.0 / disgustCount END AS joyDisgustRatio
            
                // Order by joy-to-disgust ratio to rank performers
                ORDER BY joyDisgustRatio DESC
            
                // Return ranked list of performers with total cleanings
                 RETURN r.name AS cleaner, 
                        joyDisgustRatio AS ratio, 
                        totalCleanings
                """
            result = session.run(query)
            records = [record.data() for record in result]
            columns = result.keys()

            # Create a DataFrame from the records
            df = pd.DataFrame(records, columns=columns)

            print(df)
    except Exception as e:
        print(e)


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
    identify_best_cleaners()