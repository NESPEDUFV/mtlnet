"""
Neural network components for Space2Vec spatial encoding.

Contains activation functions and feed-forward network layers
used by the GridCell spatial relation encoders.
"""

import math

import numpy as np
import torch
import torch.nn as nn


def get_activation_function(activation: str, context_str: str = "") -> nn.Module:
    """
    Factory function for activation functions.

    Args:
        activation: One of 'leakyrelu', 'relu', 'sigmoid', 'tanh', 'gelu'
        context_str: Context string for error messages

    Returns:
        PyTorch activation module
    """
    if activation == "leakyrelu":
        return nn.LeakyReLU(negative_slope=0.2)
    elif activation == "relu":
        return nn.ReLU()
    elif activation == "sigmoid":
        return nn.Sigmoid()
    elif activation == "tanh":
        return nn.Tanh()
    elif activation == "gelu":
        return nn.GELU()
    else:
        raise ValueError(f"{context_str} activation '{activation}' not recognized.")


class SingleFeedForwardNN(nn.Module):
    """
    Single layer fully connected feed forward neural network.

    Includes optional non-linearity, layer normalization, dropout, and skip connection.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        dropout_rate: float = None,
        activation: str = "sigmoid",
        use_layernormalize: bool = False,
        skip_connection: bool = False,
        context_str: str = "",
    ):
        """
        Args:
            input_dim: Input embedding dimension
            output_dim: Output dimension
            dropout_rate: Dropout probability (None for no dropout)
            activation: Activation function name
            use_layernormalize: Whether to apply layer normalization
            skip_connection: Whether to add skip connection
            context_str: Context string for error messages
        """
        super(SingleFeedForwardNN, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim

        if dropout_rate is not None:
            self.dropout = nn.Dropout(p=dropout_rate)
        else:
            self.dropout = None

        self.act = get_activation_function(activation, context_str)

        if use_layernormalize:
            self.layernorm = nn.LayerNorm(self.output_dim)
        else:
            self.layernorm = None

        # Skip connection only possible if input and output dims match
        if self.input_dim == self.output_dim:
            self.skip_connection = skip_connection
        else:
            self.skip_connection = False

        self.linear = nn.Linear(self.input_dim, self.output_dim)
        nn.init.xavier_uniform_(self.linear.weight)

    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        Args:
            input_tensor: Shape [batch_size, ..., input_dim]
        Returns:
            Tensor of shape [batch_size, ..., output_dim]
        """
        assert input_tensor.size()[-1] == self.input_dim

        output = self.linear(input_tensor)
        output = self.act(output)

        if self.dropout is not None:
            output = self.dropout(output)

        if self.skip_connection:
            output = output + input_tensor

        if self.layernorm is not None:
            output = self.layernorm(output)

        return output


class MultiLayerFeedForwardNN(nn.Module):
    """
    Multi-layer fully connected feed forward neural network.

    Stacks multiple SingleFeedForwardNN layers. Hidden layers use non-linearity,
    layer normalization, and dropout. The last layer does not.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        num_hidden_layers: int = 0,
        dropout_rate: float = None,
        hidden_dim: int = -1,
        activation: str = "sigmoid",
        use_layernormalize: bool = False,
        skip_connection: bool = False,
        context_str: str = None,
    ):
        """
        Args:
            input_dim: Input embedding dimension
            output_dim: Output dimension
            num_hidden_layers: Number of hidden layers (0 for linear network)
            dropout_rate: Dropout probability
            hidden_dim: Hidden layer dimension
            activation: Activation function name
            use_layernormalize: Whether to apply layer normalization
            skip_connection: Whether to add skip connections
            context_str: Context string for error messages
        """
        super(MultiLayerFeedForwardNN, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.num_hidden_layers = num_hidden_layers
        self.dropout_rate = dropout_rate
        self.hidden_dim = hidden_dim
        self.activation = activation
        self.use_layernormalize = use_layernormalize
        self.skip_connection = skip_connection
        self.context_str = context_str

        self.layers = nn.ModuleList()

        if self.num_hidden_layers <= 0:
            # Single linear layer
            self.layers.append(
                SingleFeedForwardNN(
                    input_dim=self.input_dim,
                    output_dim=self.output_dim,
                    dropout_rate=self.dropout_rate,
                    activation=self.activation,
                    use_layernormalize=False,
                    skip_connection=False,
                    context_str=self.context_str,
                )
            )
        else:
            # First hidden layer
            self.layers.append(
                SingleFeedForwardNN(
                    input_dim=self.input_dim,
                    output_dim=self.hidden_dim,
                    dropout_rate=self.dropout_rate,
                    activation=self.activation,
                    use_layernormalize=self.use_layernormalize,
                    skip_connection=self.skip_connection,
                    context_str=self.context_str,
                )
            )

            # Middle hidden layers
            for _ in range(self.num_hidden_layers - 1):
                self.layers.append(
                    SingleFeedForwardNN(
                        input_dim=self.hidden_dim,
                        output_dim=self.hidden_dim,
                        dropout_rate=self.dropout_rate,
                        activation=self.activation,
                        use_layernormalize=self.use_layernormalize,
                        skip_connection=self.skip_connection,
                        context_str=self.context_str,
                    )
                )

            # Output layer (no normalization or skip connection)
            self.layers.append(
                SingleFeedForwardNN(
                    input_dim=self.hidden_dim,
                    output_dim=self.output_dim,
                    dropout_rate=self.dropout_rate,
                    activation=self.activation,
                    use_layernormalize=False,
                    skip_connection=False,
                    context_str=self.context_str,
                )
            )

    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        Args:
            input_tensor: Shape [batch_size, ..., input_dim]
        Returns:
            Tensor of shape [batch_size, ..., output_dim]
        """
        assert input_tensor.size()[-1] == self.input_dim

        output = input_tensor
        for layer in self.layers:
            output = layer(output)

        return output


def cal_freq_list(
    freq_init: str,
    frequency_num: int,
    max_radius: float,
    min_radius: float,
) -> np.ndarray:
    """
    Calculate frequency list for position encoding.

    Args:
        freq_init: Initialization method ('random', 'geometric', 'nerf')
        frequency_num: Number of frequency bands
        max_radius: Maximum radius for encoding
        min_radius: Minimum radius for encoding

    Returns:
        Array of frequency values
    """
    if freq_init == "random":
        freq_list = np.random.random(size=[frequency_num]) * max_radius
    elif freq_init == "geometric":
        log_timescale_increment = math.log(float(max_radius) / float(min_radius)) / (
            frequency_num * 1.0 - 1
        )
        timescales = min_radius * np.exp(
            np.arange(frequency_num).astype(float) * log_timescale_increment
        )
        freq_list = 1.0 / timescales
    elif freq_init == "nerf":
        # NeRF position encoding: 2^{0}*pi, ..., 2^{L-1}*pi
        freq_list = np.pi * np.exp2(np.arange(frequency_num).astype(float))
    else:
        raise ValueError(f"Unknown freq_init: {freq_init}")

    return freq_list
