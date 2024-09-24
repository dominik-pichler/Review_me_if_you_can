# Init
from KG_Builder_utils.Neo4jDatabase_Handler import Neo4jDatabase_Handler
import pandas as pd

uri = "bolt://localhost:7687"  # Default port for Bolt protocol

class KG_Building_Handler:
    def __init__(self):
        self.neo4j_Handler = Neo4jDatabase_Handler(uri)
        # Can be easily extend with other databases

    def populate_KG(self,data:pd.DataFrame) -> bool:
        # Wrangling
        self.neo4j_Handler.populate_data(data)

    def populate_KG_with_demo_data(self):
        try:
            data = pd.read_csv("../data/KG_demo.csv")
            self.neo4j_Handler.populate_data(data=data)
        except Exception as e:
            raise Exception(f"Could not populate KG with demo data due to {e}")
# Continous update and Managment


# Apply/Identify Logic based connections


