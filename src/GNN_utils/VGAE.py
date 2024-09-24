import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv, VGAE
from torch_geometric.data import Data
from sklearn.cluster import KMeans
import numpy as np

# Define the encoder using GCN layers
class GCNEncoder(torch.nn.Module):
    def __init__(self, in_channels, out_channels):
        super(GCNEncoder, self).__init__()
        self.conv1 = GCNConv(in_channels, 2 * out_channels)
        self.conv2 = GCNConv(2 * out_channels, out_channels)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

# Create a VGAE model using the encoder
class MyVGAE(VGAE):
    def __init__(self, encoder):
        super(MyVGAE, self).__init__(encoder)

# Example usage:
# Define your graph data
num_nodes = 100  # Example number of nodes
num_features = 16  # Example number of features per node

# Randomly generated example data
x = torch.rand((num_nodes, num_features))  # Node features
edge_index = torch.randint(0, num_nodes, (2, num_nodes * 2))  # Random edges

data = Data(x=x, edge_index=edge_index)

# Initialize the encoder and VGAE model
encoder = GCNEncoder(in_channels=num_features, out_channels=32)
model = MyVGAE(encoder)

# Forward pass through the model to encode the nodes into latent space
model.train()
z = model.encode(data.x, data.edge_index)

# Use k-means clustering on the latent variables z
kmeans = KMeans(n_clusters=5)  # Specify the number of clusters you want
clusters = kmeans.fit_predict(z.detach().numpy())

print(f"Cluster assignments: {clusters}")

# Optionally: Evaluate cluster quality or visualize clusters if needed.