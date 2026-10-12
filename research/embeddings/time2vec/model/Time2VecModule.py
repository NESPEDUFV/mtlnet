import torch
import torch.nn as nn
import torch.nn.functional as F

from embeddings.time2vec.model.activations import SineActivation, CosineActivation


class Time2VecContrastiveModel(nn.Module):
    """
    Time2Vec model with contrastive learning for temporal embeddings.

    This model learns temporal representations using periodic activations
    and contrastive learning to capture temporal similarity patterns.
    """

    def __init__(self, activation: str = "sin", out_features: int = 64,
                 embed_dim: int = 64, in_features: int = 2):
        """
        Initialize the Time2Vec model.

        Args:
            activation: Type of periodic activation ("sin" or "cos")
            out_features: Dimension of Time2Vec output
            embed_dim: Dimension of final embedding
            in_features: Number of input time features (default: 2 for hour and dow)
        """
        super().__init__()
        self.activation_name = activation
        self.in_features = in_features
        self.out_features = out_features
        self.embed_dim = embed_dim

        if activation == "sin":
            self.time_layer = SineActivation(in_features=in_features, out_features=out_features)
        elif activation == "cos":
            self.time_layer = CosineActivation(in_features=in_features, out_features=out_features)
        else:
            raise ValueError("activation must be 'sin' or 'cos'")

        self.projector = nn.Linear(out_features, embed_dim)

    def encode(self, t: torch.Tensor) -> torch.Tensor:
        """
        Encode time features into normalized embeddings.

        Args:
            t: Tensor of shape (batch,) or (batch, in_features) with time features

        Returns:
            Normalized embeddings of shape (batch, embed_dim)
        """
        if t.dim() == 1:
            t = t.unsqueeze(-1)

        t2v = self.time_layer(t)
        z = self.projector(t2v)
        z = F.normalize(z, dim=-1)
        return z

    def forward(self, t_i: torch.Tensor, t_j: torch.Tensor):
        """
        Forward pass for contrastive learning.

        Args:
            t_i: First batch of time features
            t_j: Second batch of time features

        Returns:
            Tuple of embeddings (z_i, z_j)
        """
        z_i = self.encode(t_i)
        z_j = self.encode(t_j)
        return z_i, z_j

    def contrastive_loss(self, z_i: torch.Tensor, z_j: torch.Tensor,
                         label: torch.Tensor, tau: float = 0.3) -> torch.Tensor:
        """
        Compute contrastive loss between pairs.

        Args:
            z_i: Embeddings for first batch
            z_j: Embeddings for second batch
            label: Binary labels (1 for positive pairs, 0 for negative)
            tau: Temperature parameter

        Returns:
            Binary cross-entropy loss
        """
        sim = F.cosine_similarity(z_i, z_j)
        logits = sim / tau
        targets = label.float()
        return F.binary_cross_entropy_with_logits(logits, targets)

    def __repr__(self):
        return f'{self.__class__.__name__}(activation={self.activation_name}, out={self.out_features}, embed={self.embed_dim})'