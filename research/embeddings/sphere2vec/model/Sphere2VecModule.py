"""
Sphere2Vec-sphereM model components.

Verbatim port from the source notebook
"A General-Purpose Location Representation Learning over a Spherical Surface
for Large-Scale Geospatial Predictions (Sphere2Vec-sphereM).ipynb".

Deliberate divergences from the notebook:

1. Random seeds: the notebook sets none. The buffers in `SphereRBFPositionEncoder`
   (256 RBF centroids initialized with `torch.randn`) are non-deterministic in
   the original. This module does NOT seed internally — seeding is the caller's
   responsibility (`create_embedding` and the equivalence test do it). This
   leaves the math identical to the notebook code.

2. `device` is an explicit constructor argument with no fallback to CUDA;
   `create_embedding` defaults it from `configs.globals.DEVICE`.

3. The unused `LayerNorm` class from the notebook is dropped (the actual
   pipeline uses `nn.LayerNorm`).

Equivalence with the notebook is enforced by
`tests/test_embeddings/test_sphere2vec.py` against the frozen snapshot at
`tests/test_embeddings/_sphere2vec_reference.py`.
"""

from typing import Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def get_activation_function(activation: str, context_str: str) -> nn.Module:
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
        raise Exception("{} activation not recognized.".format(context_str))


class SingleFeedForwardNN(nn.Module):
    """
    Single fully-connected feed-forward layer with optional activation,
    dropout, layer-normalization and skip connection.

    Verbatim port from the notebook. Order of operations is:
        Linear → activation → dropout → skip → layernorm
    The skip connection is only enabled if input_dim == output_dim.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        dropout_rate: Optional[float] = None,
        activation: str = "sigmoid",
        use_layernormalize: bool = False,
        skip_connection: bool = False,
        context_str: str = "",
    ):
        super().__init__()
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

        # Skip connection only if dims match
        if self.input_dim == self.output_dim:
            self.skip_connection = skip_connection
        else:
            self.skip_connection = False

        self.linear = nn.Linear(self.input_dim, self.output_dim)
        nn.init.xavier_uniform_(self.linear.weight)

    def forward(self, input_tensor: torch.Tensor) -> torch.Tensor:
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
    Stack of `SingleFeedForwardNN` layers. The first layer maps `input_dim →
    hidden_dim`, the middle layers map `hidden_dim → hidden_dim`, and the
    final layer maps `hidden_dim → output_dim` with no activation, dropout,
    layernorm or skip applied.

    If `num_hidden_layers <= 0`, a single `input_dim → output_dim` layer is
    used.

    Verbatim port from the notebook.
    """

    def __init__(
        self,
        input_dim: int,
        output_dim: int,
        num_hidden_layers: int = 0,
        dropout_rate: Optional[float] = None,
        hidden_dim: int = -1,
        activation: str = "sigmoid",
        use_layernormalize: bool = False,
        skip_connection: bool = False,
        context_str: Optional[str] = None,
    ):
        super().__init__()
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
        assert input_tensor.size()[-1] == self.input_dim
        output = input_tensor
        for layer in self.layers:
            output = layer(output)
        return output


class SphereRBFPositionEncoder(nn.Module):
    """
    Multi-scale RBF position encoder on the unit 3-sphere.

    .. warning::
       **This is the notebook's custom RBF encoder, NOT the paper's Eq. 8
       sphereM.** The class was historically named ``SpherePositionEncoder``
       and that name is still exported as a backward-compatibility alias, but
       the "sphere" prefix is misleading — this has no architectural
       relationship to ``Sphere2Vec-sphereM`` in Mai et al. 2023. For the
       paper-faithful variant, use ``SphereMixScalePositionEncoder``.

    Steps:
        1. Convert (lat, lon) degrees to (x, y, z) on the unit sphere.
        2. Compute cosine similarity against `num_centroids` random unit
           centroids on the sphere → "distance" = 1 - cosine.
        3. Apply `num_scales` log-spaced RBF kernels:
                rbf_feat[c, s] = exp(-distance[c] * scales[s])
        4. Flatten to `[batch, num_centroids * num_scales]`.

    Both `scales` and `centroids` are stored as buffers, so they are NOT
    learned during training (this matches the notebook).

    NOTE on `device`: the buffers (`scales`, `centroids`) are created on CPU
    inside `__init__` regardless of the `device` argument — `torch.randn`
    and `torch.logspace` allocate on CPU and `register_buffer` does not move
    them. The forward pass moves the input `coords` to `self.device`, so if
    you construct with `device='mps'`/`'cuda'` but never call `.to(device)`
    on the model, you will hit a cross-device matmul error inside `forward`.
    Always call `model.to(device)` after construction (`create_embedding`
    does this automatically).
    """

    def __init__(
        self,
        min_scale: float = 1,
        max_scale: float = 1000,
        num_scales: int = 16,
        num_centroids: int = 128,
        device: str = "cpu",
    ):
        super().__init__()
        self.device = device
        self.num_scales = num_scales
        self.num_centroids = num_centroids

        scales = torch.logspace(np.log10(min_scale), np.log10(max_scale), num_scales)
        self.register_buffer("scales", scales)

        centroids = torch.randn(num_centroids, 3)
        centroids = torch.nn.functional.normalize(centroids, dim=-1)
        self.register_buffer("centroids", centroids)

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        if not torch.is_tensor(coords):
            coords = torch.tensor(coords, dtype=torch.float32).to(self.device)
        else:
            coords = coords.float().to(self.device)

        lat = coords[..., 0]
        lon = coords[..., 1]
        lat_rad = torch.deg2rad(lat)
        lon_rad = torch.deg2rad(lon)

        x = torch.cos(lat_rad) * torch.cos(lon_rad)
        y = torch.cos(lat_rad) * torch.sin(lon_rad)
        z = torch.sin(lat_rad)

        input_vec = torch.stack([x, y, z], dim=-1)

        dot_product = torch.matmul(input_vec, self.centroids.t())

        distance = 1.0 - dot_product
        weighted_dist = distance.unsqueeze(-1) * self.scales.view(1, 1, -1)

        rbf_feat = torch.exp(-weighted_dist)

        emb = rbf_feat.flatten(1)

        return emb


# Backward-compat alias: older code imports ``SpherePositionEncoder``, which
# is a misnomer (the class is an RBF encoder, not the paper's sphereM). The
# alias keeps those imports working while new code should prefer the explicit
# ``SphereRBFPositionEncoder`` name. Do NOT remove until every external
# caller has migrated.
SpherePositionEncoder = SphereRBFPositionEncoder


class SphereMixScalePositionEncoder(nn.Module):
    """
    Paper-faithful Sphere2Vec-sphereM position encoder. Direct
    reimplementation of the official ``SphereMixScaleSpatialRelationEncoder``
    class in ``gengchenmai/sphere2vec/main/SpatialRelationEncoder.py``
    (Mai et al. 2023, ``arXiv:2306.17624``).

    **Important: paper Eq. 8 vs. official code have different term counts.**

    The paper's Equation 8 defines ``PE^sphereM_S`` as the concatenation of
    *five* terms per scale:

        [ sin φ^(s), cos φ^(s)·cos λ, cos φ·cos λ^(s),
          cos φ^(s)·sin λ, cos φ·sin λ^(s) ]

    i.e. one standalone sinusoidal plus four "scaled × unscaled" products,
    for a nominal output dim of ``5·S``.

    The official ``SphereMixScaleSpatialRelationEncoder`` code concatenates
    **eight** terms per scale:

        [ sin φ^(s), cos φ^(s), sin λ^(s), cos λ^(s),            # 4 sphereC-style
          cos φ^(s)·cos λ, cos φ·cos λ^(s),                      # 4 sphereM products
          cos φ^(s)·sin λ, cos φ·sin λ^(s) ]

    — i.e. the paper's sphereC baseline (4 plain sinusoidals of the scaled
    angles) union the paper's sphereM products (minus ``sin φ^(s)`` which is
    already in the sphereC set). Output dim = ``8·S``. This is what the
    paper's authors actually ran; the paper's Eq. 8 is a strict subset. We
    follow the **code** (which is the experimentally-validated version),
    not the paper's strict Eq. 8, because that is what the plan asks for
    and what matches the reference snapshot at
    ``tests/test_embeddings/_sphere2vec_paper_reference.py``.

    Closed-form, fully deterministic — there are no learned parameters or
    random buffers in this encoder. Output dimensionality is ``8 *
    frequency_num`` (e.g. 256 for ``frequency_num=32``). The upstream class's
    ``cal_input_dim`` reports ``4 * frequency_num``, which is stale w.r.t the
    eight concatenated terms in ``forward``; we use the correct value.

    Differences from the snapshot at
    ``tests/test_embeddings/_sphere2vec_paper_reference.py``:

    1. Pure PyTorch (no numpy in the forward path), so the encoder runs on
       MPS / CUDA and supports autograd if you ever want to differentiate
       through it.
    2. Input order is ``(lat, lon)`` (matching the rest of this package's
       pipeline) rather than the upstream ``(lon, lat)``. The swap is done
       inside ``forward``.
    3. Frequency list is a registered buffer (``freq_mat``) so it follows
       ``.to(device)`` calls like any other module state. Upstream stores
       it as a plain numpy array on the module.

    Equivalence with the upstream class on fixed inputs is verified by
    ``tests/test_embeddings/test_sphere2vec.py::TestSphereMixScalePaperEncoder``.
    """

    def __init__(
        self,
        frequency_num: int = 32,
        max_radius: float = 10000,
        min_radius: float = 10,
        device: str = "cpu",
    ):
        super().__init__()
        self.device = device
        self.frequency_num = frequency_num
        self.max_radius = max_radius
        self.min_radius = min_radius

        # Geometric log-spaced frequency list, verbatim from
        # ``_cal_freq_list(..., freq_init='geometric')`` upstream:
        #     timescales = min_radius * (max_radius/min_radius)^(k/(F-1))
        #     freq       = 1 / timescales
        if frequency_num < 2:
            raise ValueError("frequency_num must be >= 2 for geometric spacing")
        log_step = np.log(float(max_radius) / float(min_radius)) / (
            frequency_num - 1
        )
        timescales = float(min_radius) * np.exp(
            np.arange(frequency_num, dtype=np.float64) * log_step
        )
        freq_list = 1.0 / timescales  # shape (F,)

        # Register as a float32 buffer so it follows `.to(device)`.
        self.register_buffer(
            "freq_mat", torch.as_tensor(freq_list, dtype=torch.float32)
        )

    @property
    def output_dim(self) -> int:
        return 8 * self.frequency_num

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """
        Args:
            coords: Tensor of shape ``(B, 2)`` with columns ``(lat, lon)``
                in **degrees** (matching the rest of this package). The
                upstream numpy reference expects ``(lon, lat)``; the swap
                is performed here so that calling conventions stay
                consistent with ``SphereRBFPositionEncoder``.

        Returns:
            Tensor of shape ``(B, 8 * frequency_num)`` in float32, on the
            same device as the module's buffers.
        """
        if not torch.is_tensor(coords):
            coords = torch.as_tensor(coords, dtype=torch.float32)
        coords = coords.float().to(self.freq_mat.device)

        # Swap to (lon, lat) to match the upstream reference's coord order.
        lat = coords[..., 0]
        lon = coords[..., 1]

        # Degrees → radians (upstream does ``coords_mat * math.pi / 180``).
        lon_rad = lon * (float(np.pi) / 180.0)
        lat_rad = lat * (float(np.pi) / 180.0)

        # Unscaled (per-point) sinusoids — shape (B,) → (B, 1) for broadcast.
        lon_single_sin = torch.sin(lon_rad).unsqueeze(-1)
        lon_single_cos = torch.cos(lon_rad).unsqueeze(-1)
        lat_single_sin = torch.sin(lat_rad).unsqueeze(-1)
        lat_single_cos = torch.cos(lat_rad).unsqueeze(-1)

        # Scaled sinusoids: (B, F) = (B, 1) * (F,)
        lon_scaled = lon_rad.unsqueeze(-1) * self.freq_mat  # (B, F)
        lat_scaled = lat_rad.unsqueeze(-1) * self.freq_mat  # (B, F)
        lon_sin = torch.sin(lon_scaled)
        lon_cos = torch.cos(lon_scaled)
        lat_sin = torch.sin(lat_scaled)
        lat_cos = torch.cos(lat_scaled)

        # Eight terms, each (B, F). Upstream concatenates along axis=-1 then
        # reshapes to ``(B, num_ctx, 8 * F)`` — here we just stack and flatten.
        # Broadcast (B, 1) singles against (B, F) scaled vectors.
        terms = [
            lat_sin,
            lat_cos,
            lon_sin,
            lon_cos,
            lat_cos * lon_single_cos,
            lat_single_cos.expand_as(lat_cos) * lon_cos,
            lat_cos * lon_single_sin,
            lat_single_cos.expand_as(lat_cos) * lon_sin,
        ]

        # Upstream stores these as (B, num_ctx=1, 1, F, 8) and flattens
        # the last two axes in row-major order, so the innermost output axis
        # is the *term index*, not the frequency index. torch.stack on the
        # new trailing axis followed by .flatten(-2) reproduces that layout
        # exactly: stacked[b, f, t] → out[b, f*8 + t].
        stacked = torch.stack(terms, dim=-1)  # (B, F, 8)
        return stacked.flatten(-2)  # (B, 8*F)


class SphereLocationEncoder(nn.Module):
    """
    Wraps a position encoder with a learnable input projection and a
    `MultiLayerFeedForwardNN` head. Output dimensionality is `spa_embed_dim`.

    Two position-encoder variants are supported via ``encoder_variant``:

    * ``"rbf"`` (default, backward-compatible) — the notebook's custom
      random-RBF-on-sphere encoder. Output dim ``num_centroids * num_scales``.
    * ``"paper"`` — the paper's closed-form Eq. 8 sphereM encoder
      (``SphereMixScalePositionEncoder``). Output dim ``8 * num_scales``.
      ``num_centroids``, ``min_scale``/``max_scale`` for the RBF kernel
      are ignored; the ``min_scale`` / ``max_scale`` role is instead played
      by ``min_radius`` / ``max_radius``. If not given, they default to
      ``min_scale`` / ``max_scale`` (same CLI knob, different semantics).

    The unused `extent` and `interval` arguments are kept for signature
    compatibility with the notebook source.
    """

    def __init__(
        self,
        spa_embed_dim: int = 64,
        num_scales: int = 16,
        min_scale: float = 1,
        max_scale: float = 1000,
        num_centroids: int = 128,
        ffn_hidden_dim: int = 256,
        device: str = "cpu",
        extent=None,
        interval=None,
        ffn_num_hidden_layers: int = 1,
        ffn_dropout_rate: float = 0.5,
        ffn_act: str = "relu",
        ffn_use_layernormalize: bool = True,
        ffn_skip_connection: bool = True,
        encoder_variant: str = "rbf",
        min_radius: Optional[float] = None,
        max_radius: Optional[float] = None,
    ):
        super().__init__()
        self.device = device
        self.encoder_variant = encoder_variant

        if encoder_variant == "rbf":
            self.position_encoder = SphereRBFPositionEncoder(
                min_scale=min_scale,
                max_scale=max_scale,
                num_scales=num_scales,
                num_centroids=num_centroids,
                device=device,
            )
            input_dim = num_centroids * num_scales
        elif encoder_variant == "paper":
            # Reuse min_scale/max_scale as min_radius/max_radius unless the
            # caller passed explicit radii. These play the same "log-spaced
            # frequency range" role but have different paper-faithful
            # default magnitudes.
            eff_min_radius = min_radius if min_radius is not None else min_scale
            eff_max_radius = max_radius if max_radius is not None else max_scale
            self.position_encoder = SphereMixScalePositionEncoder(
                frequency_num=num_scales,
                min_radius=eff_min_radius,
                max_radius=eff_max_radius,
                device=device,
            )
            input_dim = self.position_encoder.output_dim  # 8 * num_scales
        else:
            raise ValueError(
                f"encoder_variant must be 'rbf' or 'paper', got {encoder_variant!r}"
            )

        self.input_projector = nn.Linear(input_dim, ffn_hidden_dim)

        self.ffn = MultiLayerFeedForwardNN(
            input_dim=ffn_hidden_dim,
            output_dim=spa_embed_dim,
            num_hidden_layers=ffn_num_hidden_layers,
            dropout_rate=ffn_dropout_rate,
            hidden_dim=ffn_hidden_dim,
            activation=ffn_act,
            use_layernormalize=ffn_use_layernormalize,
            skip_connection=ffn_skip_connection,
            context_str="Sphere2Vec",
        )

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        feat = self.position_encoder(coords)
        feat = self.input_projector(feat)
        out = self.ffn(feat)
        return out


class SphereLocationContrastiveModel(nn.Module):
    """
    Top-level model: `SphereLocationEncoder` followed by a 128 → `embed_dim`
    projection and final L2 normalization.

    Notebook defaults are reproduced exactly:
        spa_embed_dim=128, num_scales=32, min_scale=10, max_scale=1e7,
        num_centroids=256, ffn_hidden_dim=512.
    The `device` argument defaults to "cpu" (the notebook used CUDA when
    available, but `create_embedding` passes `args.device` explicitly).
    """

    def __init__(
        self,
        embed_dim: int = 64,
        spa_embed_dim: int = 128,
        num_scales: int = 32,
        min_scale: float = 10,
        max_scale: float = 1e7,
        num_centroids: int = 256,
        ffn_hidden_dim: int = 512,
        ffn_num_hidden_layers: int = 1,
        ffn_dropout_rate: float = 0.5,
        ffn_act: str = "relu",
        ffn_use_layernormalize: bool = True,
        ffn_skip_connection: bool = True,
        device: str = "cpu",
        encoder_variant: str = "rbf",
        min_radius: Optional[float] = None,
        max_radius: Optional[float] = None,
    ):
        super().__init__()
        self.encoder_variant = encoder_variant
        self.encoder = SphereLocationEncoder(
            spa_embed_dim=spa_embed_dim,
            num_scales=num_scales,
            min_scale=min_scale,
            max_scale=max_scale,
            num_centroids=num_centroids,
            ffn_hidden_dim=ffn_hidden_dim,
            ffn_num_hidden_layers=ffn_num_hidden_layers,
            ffn_dropout_rate=ffn_dropout_rate,
            ffn_act=ffn_act,
            ffn_use_layernormalize=ffn_use_layernormalize,
            ffn_skip_connection=ffn_skip_connection,
            device=device,
            encoder_variant=encoder_variant,
            min_radius=min_radius,
            max_radius=max_radius,
        )
        self.projector = nn.Linear(spa_embed_dim, embed_dim)

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        z = self.encoder(coords)
        z = self.projector(z)
        return torch.nn.functional.normalize(z, dim=-1)


def contrastive_bce(
    z_i: torch.Tensor,
    z_j: torch.Tensor,
    label: torch.Tensor,
    tau: float = 0.1,
) -> torch.Tensor:
    """
    Binary cross-entropy on cosine-similarity logits scaled by temperature.

    Verbatim port from the notebook.
    """
    sim = F.cosine_similarity(z_i, z_j)
    logits = sim / tau
    targets = label.float().to(z_i.device)
    return F.binary_cross_entropy_with_logits(logits, targets)
