# Init
from KG_Builder_utils.Neo4jDatabase_Handler import Neo4jDatabase_Handler
import pandas as pd
from datetime import datetime, timedelta

uri = "bolt://localhost:7687"  # Default port for Bolt protocol


class KG_Building_Handler:
    def __init__(self):
        self.neo4j_Handler = Neo4jDatabase_Handler(uri)
        # Can be easily extend with other databases

    def fetch_new_data(self, delta_timestep=2, init_load=False) -> pd.DataFrame:
        if not init_load:
            today = datetime.now()
            since_delta = today - timedelta(days=delta_timestep)
            since_delta = since_delta.strftime('%Y-%m-%d %H:%M:%S')
        else:
            since_delta = '2000-01-01 00:00:00'  # Should be adjusted to the date right before that first abt entry.
        # TODO: Integrate DB Fetch

        return None

    def populate_Neo4j_KG(self, data: pd.DataFrame) -> bool:
        # Wrangling
        self.neo4j_Handler.populate_data(data)

    def populate_Neo4j_KG_with_demo_data(self):
        try:
            data = pd.read_csv("../data/KG_demo.csv")
            self.neo4j_Handler.populate_data(data=data)
        except Exception as e:
            raise Exception(f"Could not populate KG with demo data due to {e}")
