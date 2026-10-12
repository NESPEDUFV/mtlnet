"""
Frozen verbatim snapshot of ``SphereMixScaleSpatialRelationEncoder`` from the
official Sphere2Vec repository.

Source: https://raw.githubusercontent.com/gengchenmai/sphere2vec/main/main/SpatialRelationEncoder.py

This file is the oracle against which
``research/embeddings/sphere2vec/model/Sphere2VecModule.py::SphereMixScalePositionEncoder``
is tested for bit-equivalence on fixed inputs. **Do not modify.** If the
upstream code changes, add a new snapshot file rather than editing this one.

Notes on the upstream code (preserved here verbatim for fidelity):

1. ``cal_input_dim`` returns ``coord_dim * frequency_num * 2 = 4 * frequency_num``
   but the actual ``forward`` output dimensionality is ``8 * frequency_num``
   (eight concatenated terms). The ``cal_input_dim`` result is stale w.r.t
   the ``forward`` body. The real output dim used downstream is
   ``8 * frequency_num``.

2. The eight terms concatenated in ``make_input_embeds`` are:
       [lat_sin, lat_cos, lon_sin, lon_cos,
        lat_cos * lon_single_cos, lat_single_cos * lon_cos,
        lat_cos * lon_single_sin, lat_single_cos * lon_sin]
   where ``*_sin`` / ``*_cos`` without ``single`` are computed at the scaled
   angle (``coord * freq``) and ``*_single_*`` are computed at the raw angle.
   This is the Sphere2Vec paper Eq. 8 family (``φ^(s)``/``λ^(s)``) plus the
   four plain sinusoidal terms used by the ``sphereC+`` family.

3. ``freq_init='geometric'`` (default) produces
       timescales = min_radius * (max_radius/min_radius)^(k/(F-1)), k=0..F-1
       freq = 1 / timescales
   i.e. a log-spaced frequency list between ``1/max_radius`` and ``1/min_radius``.

4. Coordinate order in the upstream code is ``(lon, lat)`` — index 0 is
   longitude, index 1 is latitude. Our pipeline uses ``(lat, lon)`` — this
   reference file is pure snapshot, and the production
   ``SphereMixScalePositionEncoder`` accepts ``(lat, lon)`` and swaps internally.
"""

import math

import numpy as np
import torch
import torch.nn as nn


def _cal_freq_list(freq_init, frequency_num, max_radius, min_radius):
    if freq_init == "random":
        freq_list = np.random.random(size=[frequency_num]) * max_radius
    elif freq_init == "geometric":
        log_timescale_increment = (
            math.log(float(max_radius) / float(min_radius))
            / (frequency_num * 1.0 - 1)
        )
        timescales = min_radius * np.exp(
            np.arange(frequency_num).astype(float) * log_timescale_increment
        )
        freq_list = 1.0 / timescales
    elif freq_init == "nerf":
        freq_list = np.pi * np.exp2(np.arange(frequency_num).astype(float))
    return freq_list


class SphereMixScaleSpatialRelationEncoder(nn.Module):
    """
    Given a list of (deltaX,deltaY), encode them using the position encoding function
    """

    def __init__(
        self,
        spa_embed_dim,
        coord_dim=2,
        frequency_num=16,
        max_radius=10000,
        min_radius=10,
        freq_init="geometric",
        ffn=None,
        device="cuda",
    ):
        super(SphereMixScaleSpatialRelationEncoder, self).__init__()
        self.spa_embed_dim = spa_embed_dim
        self.coord_dim = coord_dim
        self.frequency_num = frequency_num
        self.freq_init = freq_init
        self.max_radius = max_radius
        self.min_radius = min_radius
        self.cal_freq_list()
        self.cal_freq_mat()
        self.input_embed_dim = self.cal_input_dim()
        self.ffn = ffn
        self.device = device

    def cal_input_dim(self):
        return int(self.coord_dim * self.frequency_num * 2)

    def cal_freq_list(self):
        self.freq_list = _cal_freq_list(
            self.freq_init, self.frequency_num, self.max_radius, self.min_radius
        )

    def cal_freq_mat(self):
        freq_mat = np.expand_dims(self.freq_list, axis=1)
        self.freq_mat = freq_mat

    def make_input_embeds(self, coords):
        if type(coords) == np.ndarray:
            assert self.coord_dim == np.shape(coords)[2]
            coords = list(coords)
        elif type(coords) == list:
            assert self.coord_dim == len(coords[0][0])
        else:
            raise Exception("Unknown coords data type")

        coords_mat = np.asarray(coords).astype(float)
        batch_size = coords_mat.shape[0]
        num_context_pt = coords_mat.shape[1]
        coords_mat = np.expand_dims(coords_mat, axis=3)
        coords_mat = np.expand_dims(coords_mat, axis=4)
        coords_mat = np.repeat(coords_mat, self.frequency_num, axis=3)

        coords_mat = coords_mat * math.pi / 180

        lon_single = np.expand_dims(coords_mat[:, :, 0, :, :], axis=2)
        lat_single = np.expand_dims(coords_mat[:, :, 1, :, :], axis=2)

        lon_single_sin = np.sin(lon_single)
        lon_single_cos = np.cos(lon_single)
        lat_single_sin = np.sin(lat_single)
        lat_single_cos = np.cos(lat_single)

        spr_embeds = coords_mat * self.freq_mat
        lon = np.expand_dims(spr_embeds[:, :, 0, :, :], axis=2)
        lat = np.expand_dims(spr_embeds[:, :, 1, :, :], axis=2)

        lon_sin = np.sin(lon)
        lon_cos = np.cos(lon)
        lat_sin = np.sin(lat)
        lat_cos = np.cos(lat)

        spr_embeds_ = np.concatenate(
            [
                lat_sin,
                lat_cos,
                lon_sin,
                lon_cos,
                lat_cos * lon_single_cos,
                lat_single_cos * lon_cos,
                lat_cos * lon_single_sin,
                lat_single_cos * lon_sin,
            ],
            axis=-1,
        )

        spr_embeds = np.reshape(spr_embeds_, (batch_size, num_context_pt, -1))
        return spr_embeds

    def forward(self, coords):
        spr_embeds = self.make_input_embeds(coords)
        spr_embeds = torch.FloatTensor(spr_embeds).to(self.device)
        if self.ffn is not None:
            return self.ffn(spr_embeds)
        else:
            return spr_embeds
