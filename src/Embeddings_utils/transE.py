from neo4j import GraphDatabase
from sklearn.cluster import KMeans
import torch
from torch_geometric.data import Data
import pandas as pd
from torch_geometric.nn import TransE
import torch.optim as optim
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import plotly.graph_objs as go
import plotly.offline as pyo

# Connect to the Neo4j database
uri = "bolt://localhost:7687"
username = "neo4j"
password = "password"
driver = GraphDatabase.driver(uri, auth=(username, password))

# Define a function to fetch relevant triples
def fetch_triples():
    query = """
    MATCH (a:Appartment)<-[:IN_APPARTMENT]-(b:Booking)-[:HAS_REVIEW]->(rev:review)
    MATCH (rev)-[:HAS_EMOTION]->(em:emotion)
    RETURN a.name AS apartment_name, b.booking_id AS booking_id, rev.text AS review_text, em.text AS emotion_text
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record["apartment_name"], record["booking_id"], record["review_text"], record["emotion_text"]) for record in result]

triples = fetch_triples()
driver.close()

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(triples, columns=["apartment_name", "booking_id", "review_text", "emotion_text"])

# Create mappings for entities and relations
entity_to_id = {}
relation_to_id = {"HAS_REVIEW": 0, "HAS_EMOTION": 1}
current_entity_id = 0


def get_or_create_entity_id(entity):
    global current_entity_id
    if entity not in entity_to_id:
        entity_to_id[entity] = current_entity_id
        current_entity_id += 1
    return entity_to_id[entity]


# Generate triples with IDs
triples_with_ids = []
for _, row in df.iterrows():
    apartment_id = get_or_create_entity_id(row["apartment_name"])
    booking_id = get_or_create_entity_id(row["booking_id"])
    review_id = get_or_create_entity_id(row["review_text"])
    emotion_id = get_or_create_entity_id(row["emotion_text"])

    triples_with_ids.append((apartment_id, relation_to_id["HAS_REVIEW"], review_id))
    triples_with_ids.append((review_id, relation_to_id["HAS_EMOTION"], emotion_id))

# Example data preparation
edge_index = torch.tensor([[0, 1], [1, 2]], dtype=torch.long)  # Example edge indices
edge_type = torch.tensor([0, 1], dtype=torch.long)  # Example edge types

data = Data(edge_index=edge_index, edge_type=edge_type)

model = TransE(num_nodes=data.num_nodes, num_relations=len(set(edge_type.numpy())), hidden_channels=50)


loader = model.loader(
    head_index=data.edge_index[0],
    rel_type=data.edge_type,
    tail_index=data.edge_index[1],
    batch_size=1000,
    shuffle=True,
)



# Define optimizer
optimizer = optim.Adam(model.parameters(), lr=0.01)

# Training loop
def train():
    model.train()
    total_loss = 0
    for head_index, rel_type, tail_index in loader:
        optimizer.zero_grad()
        # Calculate loss using all required arguments
        loss = model.loss(head_index=head_index, rel_type=rel_type, tail_index=tail_index)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss

# Run training loop
for epoch in range(100):
    loss = train()
    print(f'Epoch {epoch+1}, Loss: {loss:.4f}')



# Get node embeddings from the model
embeddings = model.node_emb.weight.detach().cpu().numpy()


def plot_3d(data):
    if data.shape[0] != 3:
        raise ValueError("Input data must have shape (3, n).")

        # Extract the three sets of data points
    x_data = data[0]
    y_data = data[1]
    z_data = data[2]

    # Create a 3D scatter plot
    trace = go.Scatter3d(
        x=x_data,
        y=y_data,
        z=z_data,
        mode='markers',
        marker=dict(
            size=5,
            color='blue',  # Color of the markers
            opacity=0.8
        )
    )

    # Define the layout of the plot
    layout = go.Layout(
        title='Interactive 3D Scatter Plot',
        scene=dict(
            xaxis=dict(title='X Axis'),
            yaxis=dict(title='Y Axis'),
            zaxis=dict(title='Z Axis')
        )
    )

    # Create the figure and display it
    fig = go.Figure(data=[trace], layout=layout)
    pyo.plot(fig)

# Example usage with random data
plot_3d(embeddings)




# Apply KMeans clustering on embeddings
num_clusters = 2  # Define the number of clusters you want
kmeans = KMeans(n_clusters=num_clusters)
clusters = kmeans.fit_predict(embeddings.T)

# Print cluster assignments for each node (entity)
for entity, cluster in zip(entity_to_id.keys(), clusters):
    print(f"Entity: {entity}, Cluster: {cluster}")