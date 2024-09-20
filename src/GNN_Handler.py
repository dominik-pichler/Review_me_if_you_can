import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

# Just Balance GNN
class JBGNN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes):
        super(JBGNN, self).__init__()
        self.conv1 = GCNConv(num_node_features, 16)
        self.conv2 = GCNConv(16, num_classes)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

class DMoN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes):
        super(DMoN, self).__init__()
        self.conv1 = GCNConv(num_node_features, 16)
        self.pool = torch.nn.Linear(16, num_classes)  # Simplified pooling layer

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        s = F.softmax(self.pool(x), dim=1)  # Cluster assignment matrix
        return s


class ClusterGNN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes):
        super(ClusterGNN, self).__init__()
        self.conv1 = GCNConv(num_node_features, 64)
        self.conv2 = GCNConv(64, num_classes)

    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        x = self.conv2(x, edge_index)
        return F.log_softmax(x, dim=1)

model_jbgnn = JBGNN(num_node_features=3, num_classes=2)
model_dmon = DMoN(num_node_features=3, num_classes=2)
model_clusterGnn = ClusterGNN(num_node_features=3, num_classes=2)

model.eval()

# Prepare your data
node_features = ...  # Your node feature matrix
edge_index = ...     # Your edge list or adjacency matrix

# Make predictions
with torch.no_grad():
    soft_assignments = model(node_features, edge_index)
    cluster_labels = torch.argmax(soft_assignments, dim=1)

print("Cluster Labels:", cluster_labels)

