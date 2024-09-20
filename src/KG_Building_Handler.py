# Init
from knowlege_graph_builder_utils.Neo4jDatabase_Handler import Neo4jDatabase_Handler
import pandas as pd

uri = "bolt://localhost:7687"  # Default port for Bolt protocol

class KG_Building_Handler:
    def __init__(self):
        self.neo4j_Handler = Neo4jDatabase_Handler(uri)
        # Can be easily extend with other databases

    def populate_KG(self,data:pd.DataFrame) -> bool:
        # Wrangling
        self.neo4j_Handler.populate_data(data)


# Continous update and Managment


# Apply/Identify Logic based connections


