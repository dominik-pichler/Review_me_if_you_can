from neo4j import GraphDatabase

# Replace these with your Neo4j connection details
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_booking(self, booking_id, start_date_of_stay, appartement, cleaner, review_text, sentiment_scores,
                       issue_entities, issue_entities_adjectives):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_link_nodes,
                                      booking_id,
                                      start_date_of_stay,
                                      appartement,
                                      cleaner,
                                      review_text,
                                      sentiment_scores,
                                      issue_entities,
                                      issue_entities_adjectives)

    @staticmethod
    def _create_and_link_nodes(tx, booking_id, start_date_of_stay, appartement, cleaner, review_text, sentiment_scores,
                               issue_entities, issue_entities_adjectives):
        # Create Booking Node
        tx.run("""
            MERGE (b:Booking {id: $booking_id})
            SET b.start_date_of_stay = $start_date_of_stay,
                b.appartement = $appartement,
                b.cleaner = $cleaner,
                b.review_text = $review_text
        """, booking_id=booking_id,
               start_date_of_stay=start_date_of_stay,
               appartement=appartement,
               cleaner=cleaner,
               review_text=review_text)

        # Create Sentiment Score Nodes and Relationships
        for score in sentiment_scores:
            tx.run("""
                MERGE (s:Sentiment {score: $score})
                MERGE (b:Booking {id: $booking_id})
                MERGE (b)-[:HAS_SENTIMENT]->(s)
            """, score=score['score'], booking_id=booking_id)

        # Create Issue Entity Nodes and Relationships
        for entity in issue_entities:
            tx.run("""
                MERGE (i:IssueEntity {entity: $entity})
                MERGE (b:Booking {id: $booking_id})
                MERGE (b)-[:HAS_ISSUE_ENTITY]->(i)
            """, entity=entity['entity'], booking_id=booking_id)

        # Create Issue Entity Adjective Nodes and Relationships
        for adjective in issue_entities_adjectives:
            tx.run("""
                MERGE (a:IssueEntityAdjective {adjective: $adjective})
                MERGE (b:Booking {id: $booking_id})
                MERGE (b)-[:HAS_ISSUE_ENTITY_ADJECTIVE]->(a)
            """, adjective=adjective['adjective'], booking_id=booking_id)


def main():
    # Example data; replace with your actual data retrieval logic
    bookings = [
        {
            "Booking_ID": "1",
            "Start_date_of_stay": "2023-09-01",
            "Appartement": "A101",
            "Cleaner": "John Doe",
            "Review Text": "Great stay!",
            "Sentiment Scores": [{"score": 0.9}],
            "Issue_Entities": [{"entity": "noise"}],
            "Issue_Entities_Adjectives": [{"adjective": "loud"}]
        }
    ]

    neo4j_handler = Neo4jHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    for booking in bookings:
        neo4j_handler.create_booking(
            booking["Booking_ID"],
            booking["Start_date_of_stay"],
            booking["Appartement"],
            booking["Cleaner"],
            booking["Review Text"],
            booking["Sentiment Scores"],
            booking["Issue_Entities"],
            booking["Issue_Entities_Adjectives"]
        )

    neo4j_handler.close()


if __name__ == "__main__":
    main()