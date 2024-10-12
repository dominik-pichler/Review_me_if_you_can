import pandas as pd
import pandas as pd
from pykeen.datasets import PathDataset
from pykeen.pipeline import pipeline
from neo4j import GraphDatabase
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline
from pykeen.evaluation import RankBasedEvaluator
import pandas as pd
from itertools import product
from pykeen.predict import predict_all
import torch



uri = "bolt://localhost:7687"  # Update with your Neo4j URI
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))  # Update with your credentials


def fetch_triples():
    query = """
  MATCH (rev:Review)-[:indicates_perceived_cleaning_quality]->(ca:Quality_Indication)
    RETURN rev.text AS Review_Text, 
           "indicates_perceived_cleaning_quality",
           ca.text as  Quality_Indication
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record["Review_Text"], "indicates_perceived_cleaning_quality", record["Quality_Indication"]) for
                record in result]
def fetch_reviews_without_quality_connection():
    pre_predictions = []

    query = """
    MATCH (rev:Review)

     // Use OPTIONAL MATCH to find existing connections
     OPTIONAL MATCH (rev)-[:indicates_perceived_cleaning_quality]->(ca:Quality_Indication)

     // Filter out reviews and cleaners that have these connections
     WHERE ca IS NULL

      RETURN rev.text AS Review_Text"""
    with driver.session() as session:
        result = session.run(query)
        for record in result:
            review_text = record["Review_Text"]

            # Add to predictions dictionary
            if review_text not in pre_predictions:
                pre_predictions.append(review_text)

    # Close the driver connection
    driver.close()

    return pre_predictions


def fetch_unique_quality_types():
    query = """
    MATCH (n:Quality_Indication)
    RETURN DISTINCT n.text AS Quality_Indication
    """
    with driver.session() as session:
        result = session.run(query)
        return [record["Quality_Indication"] for record in result]


def process_reviews_and_predict(model):
    # Fetch reviews without quality connections
    reviews_wo_relation = fetch_reviews_without_quality_connection()
    print("Reviews without relation:", reviews_wo_relation)

    # Create a DataFrame from the reviews
    df = pd.DataFrame(reviews_wo_relation, columns=['Review_Text'])
    df['relationship'] = 'indicates_perceived_cleaning_quality'

    # Fetch unique quality types (relations)
    relations = fetch_unique_quality_types()

    print("DataFrame of reviews:", df)

    # Generate all combinations of Review_Text, relationship, and relations
    combinations = list(product(df['Review_Text'], relations))

    # Convert combinations to a DataFrame
    df_combinations = pd.DataFrame(combinations, columns=['head', 'tail'])
    df_combinations.insert(1, 'relation', 'indicates_perceived_cleaning_quality')

    # Create a TriplesFactory from the labeled triples
    pred_dataset = TriplesFactory.from_labeled_triples(
        triples=df_combinations[['head', 'relation', 'tail']].values,
        create_inverse_triples=False  # Set according to your needs
    )

    # Ensure all entities and relations are mapped correctly

    print("Max index in input tensor:", torch.max(pred_dataset.mapped_triples))
    print("Min index in input tensor:", torch.min(pred_dataset.mapped_triples))

    # Predict triples using the model
    pack = predict_all(model=model) #, triples=pred_dataset.mapped_triples)

    pred = pack.process(factory=result.training)
    pred_annotated = pred.add_membership_columns(training=result.training)
    t = pred_annotated.df
    t.to_csv("Test.csv")
    ad = pred_annotated.df

    return pack

if __name__ == '__main__':


    triple = fetch_triples()
    df = pd.DataFrame(triple, columns=['Review_Text', 'indicates_perceived_cleaning_quality', 'Quality_Indication'])

    # Assuming your dataframe has columns 'subject', 'predicate', 'object'
    triples_factory = TriplesFactory.from_labeled_triples(
        triples=df[['Review_Text', 'indicates_perceived_cleaning_quality', 'Quality_Indication']].values,
    )

    training = triples_factory
    validation = triples_factory
    testing = triples_factory

    d = training
    id_to_entity = {v: k for k, v in d.entity_to_id.items()}
    id_to_relation = {v: k for k, v in d.relation_to_id.items()}

    
    
    result = pipeline(
        model='TransE',
        loss="softplus",
        training=training,
        testing=testing,
        validation=validation,
        model_kwargs=dict(embedding_dim=3),  # Increase the embedding dimension
        optimizer_kwargs=dict(lr=0.1),  # Adjust the learning rate
        training_kwargs=dict(num_epochs=1, use_tqdm_batch=False),  # TODO: Increase the number of epochs
    )

    # The trained model is stored in the pipeline result
    model = result.model

    pack = process_reviews_and_predict(model=result.model)

