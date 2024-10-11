from neo4j import GraphDatabase
import torch
from torch_geometric.nn import TransE
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn

# Connect to the Neo4j database
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"
driver = GraphDatabase.driver(uri, auth=(username, password))


# Define a function to fetch relevant triples
def fetch_triples():
    query = """
    MATCH (rev:Review)-[:HAS_PERCEIVED_CLEANING]->(ca:PerceivedCleaningQuality)-[:INDICATES_CLEANING_QUALITY]->(r:Reinigungsmitarbeiter)
    RETURN rev.text AS Review_Text, 
           ca.text AS Perceived_Cleaning_Quality,
           r.name AS ReinigungsMitarbeiter
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record["Review_Text"], record["Perceived_Cleaning_Quality"], record["ReinigungsMitarbeiter"]) for
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


def fetch_unique_quality_types():
    query = """
    MATCH(n: PerceivedCleaningQuality)
    RETURN
    DISTINCT n
    """
    with driver.session() as session:
        result = session.run(query)
        return [list(record["n"].labels) for record in result]


# Step 2: Preprocess data
class TripleDataset(Dataset):
    def __init__(self, triples):
        self.entities = set()
        self.relations = set()
        for h, r, t in triples:
            self.entities.add(h)
            self.entities.add(t)
            self.relations.add(r)

        self.entity_to_idx = {entity: idx for idx, entity in enumerate(self.entities)}
        self.relation_to_idx = {relation: idx for idx, relation in enumerate(self.relations)}

        self.triples = [(self.entity_to_idx[h], self.relation_to_idx[r], self.entity_to_idx[t]) for h, r, t in triples]

    def __len__(self): return len(self.triples)

    def __getitem__(self, idx): return self.triples[idx]

triples = fetch_triples();driver.close()
dataset = TripleDataset(triples)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)


class TransE(nn.Module):
    def __init__(self, num_entities, num_relations, embedding_dim):
        super(TransE, self).__init__()
        self.entity_embeddings = nn.Embedding(num_entities, embedding_dim)
        self.relation_embeddings = nn.Embedding(num_relations, embedding_dim)

    def forward(self, head_idxs, relation_idxs, tail_idxs):
        head_embeds = self.entity_embeddings(head_idxs)
        relation_embeds = self.relation_embeddings(relation_idxs)
        tail_embeds = self.entity_embeddings(tail_idxs)

        score = torch.norm(head_embeds + relation_embeds - tail_embeds, p=1, dim=1)
        return score


def predict_missing_links(model, entity_to_idx, relation_to_idx, reviews, cleaners, perceived_qualities, top_k=1):
    # Convert relation names to indices
    has_perceived_cleaning_idx = relation_to_idx["HAS_PERCEIVED_CLEANING"]
    indicates_cleaning_quality_idx = relation_to_idx["INDICATES_CLEANING_QUALITY"]

    # Prepare results dictionary
    predictions = {"reviews": {}, "cleaners": {}}

    # Predict missing links for reviews
    for review in reviews:
        if review not in entity_to_idx:
            continue
        review_idx = torch.tensor([entity_to_idx[review]], dtype=torch.long)
        all_quality_indices = torch.tensor([entity_to_idx[quality] for quality in perceived_qualities],
                                           dtype=torch.long)

        with torch.no_grad():
            scores = model(review_idx.repeat(len(all_quality_indices)),
                           torch.tensor([has_perceived_cleaning_idx] * len(all_quality_indices), dtype=torch.long),
                           all_quality_indices)

        _, top_quality_indices = torch.topk(scores, k=top_k, largest=False)
        idx_to_entity = {idx: entity for entity, idx in entity_to_idx.items()}
        top_qualities = [idx_to_entity[idx.item()] for idx in top_quality_indices]

        predictions["reviews"][review] = top_qualities

    # Predict missing links for cleaners
    for cleaner in cleaners:
        if cleaner not in entity_to_idx:
            continue
        cleaner_idx = torch.tensor([entity_to_idx[cleaner]], dtype=torch.long)

        with torch.no_grad():
            scores = model(all_quality_indices,
                           torch.tensor([indicates_cleaning_quality_idx] * len(all_quality_indices), dtype=torch.long),
                           cleaner_idx.repeat(len(all_quality_indices)))

        _, top_quality_indices = torch.topk(scores, k=top_k, largest=False)
        top_qualities = [idx_to_entity[idx.item()] for idx in top_quality_indices]

        predictions["cleaners"][cleaner] = top_qualities

    return predictions


if __name__ == '__main__':

    num_entities = len(dataset.entities)
    num_relations = len(dataset.relations)
    embedding_dim = 100

    model = TransE(num_entities=num_entities, num_relations=num_relations, embedding_dim=embedding_dim)
    optimizer = optim.SGD(model.parameters(), lr=0.01)

    for epoch in range(100):  # Number of epochs
        total_loss = 0
        for head_idxs, relation_idxs, tail_idxs in dataloader:
            optimizer.zero_grad()
            loss = model(head_idxs, relation_idxs, tail_idxs).sum()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f'Epoch {epoch + 1}, Loss: {total_loss}')

    reviews_without_quality_connection = fetch_reviews_without_quality_connection()
    # Example usage:
    reviews = reviews_without_quality_connection["reviews"]
    cleaners = reviews_without_quality_connection["cleaners"]
    perceived_qualities = fetch_unique_quality_types()

    predictions = predict_missing_links(model, dataset.entity_to_idx, dataset.relation_to_idx, reviews, cleaners,perceived_qualities)

    print("Predicted connections:")
    for review, qualities in predictions["reviews"].items(): print(
        f"Review '{review}' connected to qualities: {qualities}")

    for cleaner, qualities in predictions["cleaners"].items(): print(
        f"Cleaner '{cleaner}' connected to qualities: {qualities}")
