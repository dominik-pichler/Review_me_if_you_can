from neo4j import GraphDatabase
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline
import pandas as pd
from pykeen.predict import predict_all


class TransE_Handler:
    def __init__(self):
        self.uri = "bolt://localhost:7687"
        self.driver = GraphDatabase.driver(self.uri, auth=("neo4j", "password"))

    # Used to get training data
    def fetch_triples(self):
        query = """
      MATCH (rev:Review)-[:indicates_perceived_cleaning_quality]->(ca:Quality_Indication)
        RETURN rev.text AS Review_Text, 
               "indicates_perceived_cleaning_quality",
               ca.text as  Quality_Indication
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [(record["Review_Text"], "indicates_perceived_cleaning_quality", record["Quality_Indication"]) for
                    record in result]

    # Used to get reviews for which relations should be derived
    def fetch_reviews_without_quality_connection(self):
        pre_predictions = []

        query = """
        MATCH (rev:Review)
    
         // Use OPTIONAL MATCH to find existing connections
         OPTIONAL MATCH (rev)-[:indicates_perceived_cleaning_quality]->(ca:Quality_Indication)
    
         // Filter out reviews and cleaners that have these connections
         WHERE ca IS NULL
    
          RETURN rev.text AS Review_Text"""
        with self.driver.session() as session:
            result = session.run(query)
            for record in result:
                review_text = record["Review_Text"]

                # Add to predictions dictionary
                if review_text not in pre_predictions:
                    pre_predictions.append(review_text)

        # Close the driver connection
        self.driver.close()

        return pre_predictions

    # Helper to get all unique quality indications from the raw data
    def fetch_unique_quality_types(self):
        query = """
        MATCH (n:Quality_Indication)
        RETURN DISTINCT n.text AS Quality_Indication
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record["Quality_Indication"] for record in result]

    def train_model(self):
        triple = self.fetch_triples()
        df = pd.DataFrame(triple, columns=['Review_Text', 'indicates_perceived_cleaning_quality', 'Quality_Indication'])

        # Assuming your dataframe has columns 'subject', 'predicate', 'object'
        from sklearn.model_selection import train_test_split

        # Split the data into training and testing sets
        train_triples, test_triples = train_test_split(
            df[['Review_Text', 'indicates_perceived_cleaning_quality', 'Quality_Indication']].values, test_size=0.2)

        # Further split the training data into training and validation sets
        train_triples, val_triples = train_test_split(train_triples, test_size=0.25)  # 0.25 x 0.8 = 0.2

        # Create TriplesFactory instances for each set
        training_factory = TriplesFactory.from_labeled_triples(triples=train_triples)
        validation_factory = TriplesFactory.from_labeled_triples(triples=val_triples)
        testing_factory = TriplesFactory.from_labeled_triples(triples=test_triples)

        result = pipeline(
            model='TransE',
            loss="softplus",
            training=training_factory,
            testing=testing_factory,
            validation=validation_factory,
            model_kwargs=dict(embedding_dim=3),
            optimizer_kwargs=dict(lr=0.1),  # Adjust the learning rate
            training_kwargs=dict(num_epochs=100, use_tqdm_batch=False),
        )

        self.result = result
        self.model = result.model


    # Predictor
    def predict(self,trainig_results):

        # Fetch unique quality types (relations)
        relations = self.fetch_unique_quality_types()

        # Predict triples using the model
        pack = predict_all(model=trainig_results.model) #, triples=pred_dataset.mapped_triples)

        pred = pack.process(factory=trainig_results.training)
        pred_annotated = pred.add_membership_columns(training=trainig_results.training)
        t = pred_annotated.df
        t.to_csv("Test.csv")
        judged_triples = pred_annotated.df

        # Filter DataFrame based on conditions
        filtered_df = judged_triples[
            (judged_triples['in_training'] == False) &
            (judged_triples['tail_label'].isin(relations))
            ]

        # Get row with highest score for each head_label
        result_df = filtered_df.loc[filtered_df.groupby('head_label')['score'].idxmax()]

        return result_df[["head_label","relation_label","tail_label","score"]]

if __name__ == '__main__':
        transE_Handler = TransE_Handler()
        transE_Handler.train_model()
        transE_Handler.predict(trainig_results=transE_Handler.result)

