"""
Spatial encoding models for Space2Vec.

Contains position encoders and location encoders based on GridCell spatial
relation encoding with sinusoidal position encoding similar to Transformers.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from embeddings.space2vec.model.components import (
    MultiLayerFeedForwardNN,
    cal_freq_list,
)


class PositionEncoder(nn.Module):
    """Abstract base class for position encoders."""

    def __init__(self, coord_dim: int = 2, device: str = "cpu"):
        super(PositionEncoder, self).__init__()
        self.coord_dim = coord_dim
        self.device = device
        self.pos_enc_output_dim = None

    def cal_pos_enc_output_dim(self) -> int:
        raise NotImplementedError(
            "The 'pos_enc_output_dim' property should be implemented by subclasses."
        )

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError("This method should be implemented by subclasses.")


class SpaceEncoder(nn.Module):
    """Abstract base class for space/location encoders."""

    def __init__(self, spa_embed_dim: int, coord_dim: int = 2, device: str = "cpu"):
        super(SpaceEncoder, self).__init__()
        self.spa_embed_dim = spa_embed_dim
        self.coord_dim = coord_dim
        self.device = device

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError("This method should be implemented by subclasses.")


class GridCellSpatialRelationPositionEncoder(PositionEncoder):
    """
    Encodes (deltaX, deltaY) coordinates using sinusoidal position encoding.

    Uses sine/cosine functions at multiple frequencies similar to
    Transformer positional encoding.

    Note: This is the original numpy-based implementation for compatibility.
    For faster GPU training, use GridCellPositionEncoderTorch instead.
    """

    def __init__(
        self,
        coord_dim: int = 2,
        frequency_num: int = 24,
        max_radius: float = 10000,
        min_radius: float = 10,
        freq_init: str = "geometric",
        device: str = "cpu",
    ):
        """
        Args:
            coord_dim: Dimension of coordinates (2D, 3D, etc.)
            frequency_num: Number of sinusoidal frequencies
            max_radius: Maximum context radius for encoding
            min_radius: Minimum context radius for encoding
            freq_init: Frequency initialization method
            device: Device for computations
        """
        super().__init__(coord_dim=coord_dim, device=device)
        self.frequency_num = frequency_num
        self.max_radius = max_radius
        self.min_radius = min_radius
        self.freq_init = freq_init

        self._cal_freq_list()
        self._cal_freq_mat()
        self.pos_enc_output_dim = self.cal_pos_enc_output_dim()

    def _cal_freq_list(self):
        """Calculate the frequency list for position encoding."""
        self.freq_list = cal_freq_list(
            self.freq_init, self.frequency_num, self.max_radius, self.min_radius
        )

    def _cal_freq_mat(self):
        """Create frequency matrix for vectorized computation."""
        freq_mat = np.expand_dims(self.freq_list, axis=1)
        self.freq_mat = np.repeat(freq_mat, 2, axis=1)

    def cal_pos_enc_output_dim(self) -> int:
        """Compute the dimension of the encoded spatial relation embedding."""
        return int(self.coord_dim * self.frequency_num * 2)

    def make_output_embeds(self, coords) -> np.ndarray:
        """
        Create sinusoidal position embeddings from coordinates.

        Args:
            coords: Coordinates array of shape (batch_size, num_context_pt, coord_dim)

        Returns:
            Position embeddings of shape (batch_size, num_context_pt, pos_enc_output_dim)
        """
        if isinstance(coords, np.ndarray):
            assert self.coord_dim == np.shape(coords)[2]
            coords = list(coords)
        elif isinstance(coords, list):
            assert self.coord_dim == len(coords[0][0])
        else:
            raise TypeError(
                "Unknown coords data type for GridCellSpatialRelationEncoder"
            )

        coords_mat = np.asarray(coords).astype(float)
        batch_size = coords_mat.shape[0]
        num_context_pt = coords_mat.shape[1]

        # Expand dimensions for broadcasting
        coords_mat = np.expand_dims(coords_mat, axis=3)  # (B, N, 2, 1)
        coords_mat = np.expand_dims(coords_mat, axis=4)  # (B, N, 2, 1, 1)
        coords_mat = np.repeat(coords_mat, self.frequency_num, axis=3)  # (B, N, 2, F, 1)
        coords_mat = np.repeat(coords_mat, 2, axis=4)  # (B, N, 2, F, 2)

        # Apply frequencies
        spr_embeds = coords_mat * self.freq_mat

        # Apply sin/cos: sin for 2i, cos for 2i+1
        spr_embeds[:, :, :, :, 0::2] = np.sin(spr_embeds[:, :, :, :, 0::2])
        spr_embeds[:, :, :, :, 1::2] = np.cos(spr_embeds[:, :, :, :, 1::2])

        # Reshape to (batch_size, num_context_pt, pos_enc_output_dim)
        spr_embeds = np.reshape(spr_embeds, (batch_size, num_context_pt, -1))

        return spr_embeds

    def forward(self, coords) -> torch.Tensor:
        """
        Encode coordinates using sinusoidal position encoding.

        Args:
            coords: Coordinates of shape (batch_size, num_context_pt, coord_dim)

        Returns:
            Position embeddings of shape (batch_size, num_context_pt, pos_enc_output_dim)
        """
        spr_embeds = self.make_output_embeds(coords)
        spr_embeds = torch.FloatTensor(spr_embeds).to(self.device)
        return spr_embeds


class GridCellPositionEncoderTorch(PositionEncoder):
    """
    Pure PyTorch position encoder - all operations on GPU.

    This is a faster alternative to GridCellSpatialRelationPositionEncoder
    that keeps all computations on the GPU without numpy conversions.

    Produces the same output as the numpy version but 2-3x faster during training.
    """

    def __init__(
        self,
        coord_dim: int = 2,
        frequency_num: int = 24,
        max_radius: float = 10000,
        min_radius: float = 10,
        freq_init: str = "geometric",
        device: str = "cpu",
    ):
        """
        Args:
            coord_dim: Dimension of coordinates (2D, 3D, etc.)
            frequency_num: Number of sinusoidal frequencies
            max_radius: Maximum context radius for encoding
            min_radius: Minimum context radius for encoding
            freq_init: Frequency initialization method
            device: Device for computations
        """
        super().__init__(coord_dim=coord_dim, device=device)
        self.frequency_num = frequency_num
        self.max_radius = max_radius
        self.min_radius = min_radius
        self.freq_init = freq_init
        self.pos_enc_output_dim = self.cal_pos_enc_output_dim()

        # Compute frequencies and register as buffer (moves with model to device)
        freq_list = cal_freq_list(freq_init, frequency_num, max_radius, min_radius)
        # Shape: (frequency_num,) -> (1, 1, 1, frequency_num) for broadcasting
        freq_tensor = torch.FloatTensor(freq_list).view(1, 1, 1, frequency_num)
        self.register_buffer("freq_tensor", freq_tensor)

    def cal_pos_enc_output_dim(self) -> int:
        """Compute the dimension of the encoded spatial relation embedding."""
        return int(self.coord_dim * self.frequency_num * 2)

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """
        Encode coordinates using sinusoidal position encoding (pure PyTorch).

        Args:
            coords: Coordinates tensor of shape (batch_size, num_context_pt, coord_dim)
                    or (batch_size, coord_dim) - will be unsqueezed automatically

        Returns:
            Position embeddings of shape (batch_size, num_context_pt, pos_enc_output_dim)
        """
        # Handle 2D input (batch_size, coord_dim) -> (batch_size, 1, coord_dim)
        if coords.dim() == 2:
            coords = coords.unsqueeze(1)

        # Ensure tensor is on correct device and dtype
        coords = coords.to(self.freq_tensor.device).float()

        batch_size, num_context_pt, coord_dim = coords.shape

        # Reshape for broadcasting: (B, N, D) -> (B, N, D, 1)
        coords_expanded = coords.unsqueeze(-1)  # (B, N, D, 1)

        # Multiply by frequencies: (B, N, D, 1) * (1, 1, 1, F) -> (B, N, D, F)
        angles = coords_expanded * self.freq_tensor

        # Apply sin and cos
        sin_enc = torch.sin(angles)  # (B, N, D, F)
        cos_enc = torch.cos(angles)  # (B, N, D, F)

        # Interleave sin and cos: [sin, cos] for each frequency
        # Stack and reshape: (B, N, D, F, 2) -> (B, N, D * F * 2)
        spr_embeds = torch.stack([sin_enc, cos_enc], dim=-1)  # (B, N, D, F, 2)
        spr_embeds = spr_embeds.view(batch_size, num_context_pt, -1)  # (B, N, D*F*2)

        return spr_embeds


class GridCellSpatialRelationSpaceEncoder(SpaceEncoder):
    """
    Combines GridCell position encoding with a feed-forward network.

    Architecture: Position Encoding -> FFN projection
    """

    def __init__(
        self,
        spa_embed_dim: int = 64,
        coord_dim: int = 2,
        frequency_num: int = 16,
        max_radius: float = 10000,
        min_radius: float = 10,
        freq_init: str = "geometric",
        device: str = "cpu",
        ffn_act: str = "relu",
        ffn_num_hidden_layers: int = 1,
        ffn_dropout_rate: float = 0.5,
        ffn_hidden_dim: int = 256,
        ffn_use_layernormalize: bool = True,
        ffn_skip_connection: bool = True,
        ffn_context_str: str = "GridCellSpatialRelationEncoder",
    ):
        """
        Args:
            spa_embed_dim: Output spatial embedding dimension
            coord_dim: Input coordinate dimension
            frequency_num: Number of sinusoidal frequencies
            max_radius: Maximum radius for position encoding
            min_radius: Minimum radius for position encoding
            freq_init: Frequency initialization method
            device: Device for computations
            ffn_act: Activation function for FFN
            ffn_num_hidden_layers: Number of hidden layers in FFN
            ffn_dropout_rate: Dropout rate for FFN
            ffn_hidden_dim: Hidden dimension for FFN
            ffn_use_layernormalize: Whether to use layer normalization
            ffn_skip_connection: Whether to use skip connections
            ffn_context_str: Context string for error messages
        """
        super().__init__(spa_embed_dim, coord_dim, device)
        self.frequency_num = frequency_num
        self.max_radius = max_radius
        self.min_radius = min_radius
        self.freq_init = freq_init
        self.ffn_act = ffn_act
        self.ffn_num_hidden_layers = ffn_num_hidden_layers
        self.ffn_dropout_rate = ffn_dropout_rate
        self.ffn_hidden_dim = ffn_hidden_dim
        self.ffn_use_layernormalize = ffn_use_layernormalize
        self.ffn_skip_connection = ffn_skip_connection

        self.position_encoder = GridCellSpatialRelationPositionEncoder(
            coord_dim=coord_dim,
            frequency_num=frequency_num,
            max_radius=max_radius,
            min_radius=min_radius,
            freq_init=freq_init,
            device=device,
        )

        self.ffn = MultiLayerFeedForwardNN(
            input_dim=self.position_encoder.pos_enc_output_dim,
            output_dim=self.spa_embed_dim,
            num_hidden_layers=self.ffn_num_hidden_layers,
            dropout_rate=ffn_dropout_rate,
            hidden_dim=self.ffn_hidden_dim,
            activation=self.ffn_act,
            use_layernormalize=self.ffn_use_layernormalize,
            skip_connection=ffn_skip_connection,
            context_str=ffn_context_str,
        )

    def forward(self, coords) -> torch.Tensor:
        """
        Encode coordinates through position encoder and FFN.

        Args:
            coords: Coordinates of shape (batch_size, num_context_pt, coord_dim)

        Returns:
            Spatial embeddings of shape (batch_size, num_context_pt, spa_embed_dim)
        """
        spr_embeds = self.position_encoder(coords)
        sprenc = self.ffn(spr_embeds)
        return sprenc


class GridCellSpaceEncoderTorch(SpaceEncoder):
    """
    Pure PyTorch Space Encoder - all operations on GPU.

    Combines GridCellPositionEncoderTorch with a feed-forward network.
    This is 2-3x faster than GridCellSpatialRelationSpaceEncoder during training.
    """

    def __init__(
        self,
        spa_embed_dim: int = 64,
        coord_dim: int = 2,
        frequency_num: int = 16,
        max_radius: float = 10000,
        min_radius: float = 10,
        freq_init: str = "geometric",
        device: str = "cpu",
        ffn_act: str = "relu",
        ffn_num_hidden_layers: int = 1,
        ffn_dropout_rate: float = 0.5,
        ffn_hidden_dim: int = 256,
        ffn_use_layernormalize: bool = True,
        ffn_skip_connection: bool = True,
        ffn_context_str: str = "GridCellSpaceEncoderTorch",
    ):
        """
        Args:
            spa_embed_dim: Output spatial embedding dimension
            coord_dim: Input coordinate dimension
            frequency_num: Number of sinusoidal frequencies
            max_radius: Maximum radius for position encoding
            min_radius: Minimum radius for position encoding
            freq_init: Frequency initialization method
            device: Device for computations
            ffn_act: Activation function for FFN
            ffn_num_hidden_layers: Number of hidden layers in FFN
            ffn_dropout_rate: Dropout rate for FFN
            ffn_hidden_dim: Hidden dimension for FFN
            ffn_use_layernormalize: Whether to use layer normalization
            ffn_skip_connection: Whether to use skip connections
            ffn_context_str: Context string for error messages
        """
        super().__init__(spa_embed_dim, coord_dim, device)
        self.frequency_num = frequency_num
        self.max_radius = max_radius
        self.min_radius = min_radius
        self.freq_init = freq_init
        self.ffn_act = ffn_act
        self.ffn_num_hidden_layers = ffn_num_hidden_layers
        self.ffn_dropout_rate = ffn_dropout_rate
        self.ffn_hidden_dim = ffn_hidden_dim
        self.ffn_use_layernormalize = ffn_use_layernormalize
        self.ffn_skip_connection = ffn_skip_connection

        # Use Pure PyTorch position encoder
        self.position_encoder = GridCellPositionEncoderTorch(
            coord_dim=coord_dim,
            frequency_num=frequency_num,
            max_radius=max_radius,
            min_radius=min_radius,
            freq_init=freq_init,
            device=device,
        )

        self.ffn = MultiLayerFeedForwardNN(
            input_dim=self.position_encoder.pos_enc_output_dim,
            output_dim=self.spa_embed_dim,
            num_hidden_layers=self.ffn_num_hidden_layers,
            dropout_rate=ffn_dropout_rate,
            hidden_dim=self.ffn_hidden_dim,
            activation=self.ffn_act,
            use_layernormalize=self.ffn_use_layernormalize,
            skip_connection=ffn_skip_connection,
            context_str=ffn_context_str,
        )

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """
        Encode coordinates through position encoder and FFN.

        Args:
            coords: Coordinates tensor of shape (batch_size, num_context_pt, coord_dim)
                    or (batch_size, coord_dim)

        Returns:
            Spatial embeddings of shape (batch_size, num_context_pt, spa_embed_dim)
        """
        spr_embeds = self.position_encoder(coords)
        sprenc = self.ffn(spr_embeds)
        return sprenc


class SpaceContrastiveModel(nn.Module):
    """
    Contrastive learning model for spatial location embeddings.

    Supports both numpy-based encoder (for notebook compatibility) and
    pure PyTorch encoder (for faster training).
    """

    def __init__(
        self,
        embed_dim: int = 64,
        spa_embed_dim: int = 128,
        coord_dim: int = 2,
        frequency_num: int = 16,
        max_radius: float = 50,
        min_radius: float = 0.02,
        ffn_act: str = "leakyrelu",
        freq_init: str = "geometric",
        ffn_num_hidden_layers: int = 1,
        ffn_dropout_rate: float = 0.5,
        ffn_use_layernormalize: bool = True,
        ffn_skip_connection: bool = True,
        ffn_hidden_dim: int = 512,
        device: str = "cpu",
        use_torch_encoder: bool = True,
    ):
        """
        Args:
            embed_dim: Final embedding dimension
            spa_embed_dim: Spatial encoder output dimension
            coord_dim: Input coordinate dimension
            frequency_num: Number of sinusoidal frequencies
            max_radius: Maximum radius for position encoding
            min_radius: Minimum radius for position encoding
            ffn_act: Activation function for FFN
            freq_init: Frequency initialization method
            ffn_num_hidden_layers: Number of hidden layers in FFN
            ffn_dropout_rate: Dropout rate for FFN
            ffn_use_layernormalize: Whether to use layer normalization
            ffn_skip_connection: Whether to use skip connections
            ffn_hidden_dim: Hidden dimension for FFN
            device: Device for computations
            use_torch_encoder: If True, use pure PyTorch encoder (faster).
                If False, use numpy-based encoder (notebook compatible).
        """
        super().__init__()
        self.embed_dim = embed_dim
        self.spa_embed_dim = spa_embed_dim
        self.device = device
        self.use_torch_encoder = use_torch_encoder

        # Choose encoder based on use_torch_encoder flag
        if use_torch_encoder:
            self.encoder = GridCellSpaceEncoderTorch(
                spa_embed_dim=spa_embed_dim,
                coord_dim=coord_dim,
                frequency_num=frequency_num,
                max_radius=max_radius,
                min_radius=min_radius,
                ffn_act=ffn_act,
                freq_init=freq_init,
                ffn_num_hidden_layers=ffn_num_hidden_layers,
                ffn_dropout_rate=ffn_dropout_rate,
                ffn_use_layernormalize=ffn_use_layernormalize,
                ffn_skip_connection=ffn_skip_connection,
                ffn_hidden_dim=ffn_hidden_dim,
                device=device,
            )
        else:
            self.encoder = GridCellSpatialRelationSpaceEncoder(
                spa_embed_dim=spa_embed_dim,
                coord_dim=coord_dim,
                frequency_num=frequency_num,
                max_radius=max_radius,
                min_radius=min_radius,
                ffn_act=ffn_act,
                freq_init=freq_init,
                ffn_num_hidden_layers=ffn_num_hidden_layers,
                ffn_dropout_rate=ffn_dropout_rate,
                ffn_use_layernormalize=ffn_use_layernormalize,
                ffn_skip_connection=ffn_skip_connection,
                ffn_hidden_dim=ffn_hidden_dim,
                device=device,
            )

        self.projector = nn.Linear(spa_embed_dim, embed_dim)

    def encode(self, coords: torch.Tensor) -> torch.Tensor:
        """
        Encode coordinates to normalized embeddings.

        Args:
            coords: Coordinates of shape (batch_size, 2) in XY km

        Returns:
            Normalized embeddings of shape (batch_size, embed_dim)
        """
        if self.use_torch_encoder:
            # Pure PyTorch path - no CPU/GPU transfer
            z = self.encoder(coords)
            z = z[:, 0, :]
        else:
            # Numpy path - for backward compatibility
            coords_np = coords.unsqueeze(1).cpu().numpy()
            z = self.encoder(coords_np)
            z = z[:, 0, :]

        z = self.projector(z)
        return F.normalize(z, dim=-1)

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for single coordinate batch.

        Args:
            coords: Coordinates of shape (batch_size, 2)

        Returns:
            Normalized embeddings of shape (batch_size, embed_dim)
        """
        return self.encode(coords)

    def contrastive_loss(
        self,
        z_i: torch.Tensor,
        z_j: torch.Tensor,
        label: torch.Tensor,
        tau: float = 0.1,
        loss_type: str = "bce",
    ) -> torch.Tensor:
        """
        Compute contrastive loss.

        Args:
            z_i: First set of embeddings (anchors)
            z_j: Second set of embeddings (positive/negative samples)
            label: Binary labels (1 for positive, 0 for negative)
            tau: Temperature parameter
            loss_type: Loss function type - "bce" or "infonce"

        Returns:
            Scalar loss value
        """
        if loss_type == "infonce":
            return self.info_nce_loss(z_i, z_j, label, tau)
        else:
            return self.bce_loss(z_i, z_j, label, tau)

    def bce_loss(
        self,
        z_i: torch.Tensor,
        z_j: torch.Tensor,
        label: torch.Tensor,
        tau: float = 0.1,
    ) -> torch.Tensor:
        """
        Compute binary cross-entropy contrastive loss (original implementation).

        Args:
            z_i: First set of embeddings
            z_j: Second set of embeddings
            label: Binary labels (1 for positive, 0 for negative)
            tau: Temperature parameter

        Returns:
            Scalar loss value
        """
        sim = F.cosine_similarity(z_i, z_j)
        logits = sim / tau
        targets = label.float().to(z_i.device)
        return F.binary_cross_entropy_with_logits(logits, targets)

    def info_nce_loss(
        self,
        z_i: torch.Tensor,
        z_j: torch.Tensor,
        label: torch.Tensor,
        tau: float = 0.1,
    ) -> torch.Tensor:
        """
        Compute InfoNCE loss with in-batch negatives.

        This is the standard contrastive loss used in SimCLR, MoCo, etc.
        It uses all other samples in the batch as additional negatives.

        Args:
            z_i: Anchor embeddings of shape (batch_size, embed_dim)
            z_j: Sample embeddings of shape (batch_size, embed_dim)
            label: Binary labels (1 for positive, 0 for negative)
            tau: Temperature parameter

        Returns:
            Scalar loss value
        """
        batch_size = z_i.shape[0]

        # Separate positive and negative samples
        pos_mask = label == 1
        neg_mask = label == 0

        # If no positives or no negatives, fall back to BCE
        if not pos_mask.any() or not neg_mask.any():
            return self.bce_loss(z_i, z_j, label, tau)

        # Get positive pairs
        z_anchor = z_i[pos_mask]  # (n_pos, embed_dim)
        z_pos = z_j[pos_mask]  # (n_pos, embed_dim)

        # Get all negatives for in-batch negative sampling
        z_neg = z_j[neg_mask]  # (n_neg, embed_dim)

        if z_anchor.shape[0] == 0 or z_neg.shape[0] == 0:
            return self.bce_loss(z_i, z_j, label, tau)

        # Positive similarity: (n_pos,)
        pos_sim = F.cosine_similarity(z_anchor, z_pos) / tau

        # Negative similarities: each anchor against all negatives (n_pos, n_neg)
        neg_sim = torch.mm(z_anchor, z_neg.t()) / tau

        # Combine: first column is positive, rest are negatives
        # logits: (n_pos, 1 + n_neg)
        logits = torch.cat([pos_sim.unsqueeze(1), neg_sim], dim=1)

        # Labels: 0 means the first position (positive) is the correct one
        labels = torch.zeros(z_anchor.shape[0], dtype=torch.long, device=z_i.device)

        return F.cross_entropy(logits, labels)
