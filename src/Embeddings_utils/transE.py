import pandas as pd
from pykeen.datasets import PathDataset
from pykeen.pipeline import pipeline
from neo4j import GraphDatabase
from pykeen.triples import TriplesFactory
import numpy as np
from sklearn.model_selection import train_test_split

uri = "bolt://localhost:7687"  # Update with your Neo4j URI
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))  # Update with your credentials



def fetch_triples(tx):
    query = """
    MATCH (rev:Review)-[:indicates_perceived_cleaning_quality]->(ca:Quality_Indication)
    RETURN rev.text AS Review_Text, 
         "indicates_perceived_cleaning_quality",
        ca.text AS Quality_Indication
    """
    result = tx.run(query)
    return [(record["Review_Text"], "indicates_perceived_cleaning_quality", record["Quality_Indication"]) for record in result]



# Define a function to fetch relevant triples
def fetch_triplesd():
    query = """
    MATCH (rev:Review)-[:indicates_perceived_cleaning_quality]->(ca:Quality_Indication)
    RETURN rev.text AS Review_Text, 
         "indicates_perceived_cleaning_quality",
        ca.text AS Quality_Indication
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record["Review_Text"], "indicates_perceived_cleaning_quality", record["Quality_Indication"]) for
                record in result]

def fetch_reviews_without_quality_connection():
    pre_predictions = {"reviews": {}, "cleaners": {}}

    query = """
    // Match all reviews and cleaners
    MATCH (rev:Review), (r:Reinigungsmitarbeiter)

     // Use OPTIONAL MATCH to find existing connections
     OPTIONAL MATCH (rev)-[:HAS_PERCEIVED_CLEANING]->(ca:PerceivedCleaningQuality)-[:INDICATES_CLEANING_QUALITY]->(r)

     // Filter out reviews and cleaners that have these connections
     WHERE ca IS NULL

      RETURN rev.text AS Review_Text, 
             r.name AS ReinigungsMitarbeiter
    """
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            review_text = record["Review_Text"]
            cleaner_name = record["ReinigungsMitarbeiter"]

            # Add to predictions dictionary
            if review_text not in pre_predictions["reviews"]:
                pre_predictions["reviews"][review_text] = []
            if cleaner_name not in pre_predictions["cleaners"]:
                pre_predictions["cleaners"][cleaner_name] = []

            # Add cleaner to the review's list and vice versa
            pre_predictions["reviews"][review_text].append(cleaner_name)
            pre_predictions["cleaners"][cleaner_name].append(review_text)

    # Close the driver connection
    driver.close()

    return pre_predictions



if __name__ == '__main__':
    with driver.session() as session:
        triples = session.read_transaction(fetch_triples)

    driver.close()

    # Convert list of tuples to a NumPy array
    triples_array = np.array(triples)

    assert triples_array.shape[1] == 3, "Each triple should have 3 elements (head, relation, tail)."
    # Create a TriplesFactory from the NumPy array
    triples_array = TriplesFactory.from_labeled_triples(triples_array)

    train_triples, test_triples = train_test_split(triples_array, test_size=0.2, random_state=42)

    training_factory = TriplesFactory.from_labeled_triples(train_triples)
    testing_factory = TriplesFactory.from_labeled_triples(test_triples)


    embedding_dim = 50  # Dimension of the embeddings
    scoring_fct_norm = 1  # Norm to use in the scoring function

    # Set up the pipeline for training the TransE model
    result = pipeline(
        model='TransE',
        training=training_factory,
        testing=testing_factory,
        model_kwargs=dict(
            embedding_dim=embedding_dim,
            scoring_fct_norm=scoring_fct_norm,
        ),
        training_loop='sLCWA',
        negative_sampler='basic',
        training_kwargs=dict(num_epochs=100),
    )

    # Get the trained model
    model = result.model

    # Example prediction: predict tail entity given head and relation
    head_entity = 'example_head'
    relation = 'example_relation'

    # Predict tail entities
    predicted_tails = model.predict_tails(head_entity=head_entity, relation=relation, triples_factory=result.training.triples_factory)

    print(predicted_tails)