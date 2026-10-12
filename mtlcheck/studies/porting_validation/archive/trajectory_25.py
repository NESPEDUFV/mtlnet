"""ARCHIVED one-off probe — it violates the studies contract (imports torch, runs a loop) and
is kept only because its result is cited. Its output is evidence/trajectory_25.json. Do not
extend it: a new comparison goes through the library, behind a recipe field.

5-epoch loss trajectory, port against reference, from identical weights.

Versioned because the first run of this comparison lived in /tmp and its configuration was lost —
a round-2 finding. The number it produced ("identical to ~epoch 10, max|delta| 8.3e-05 at 25") was
therefore uncheckable, which is worth less than a smaller number that can be re-derived.

Hard negatives are OFF on both sides. The port draws them vectorised (S17) and the reference in a
Python loop, so with the branch ON the two consume the RNG differently and the comparison would
measure a deliberate change rather than an implementation difference. With it OFF the streams
coincide and the trajectory isolates arithmetic.

    ARTIFACTS=/dados/poimtlnet python studies/porting_validation/scripts/trajectory_25.py
"""
import json
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import torch
from torch.nn.utils import clip_grad_norm_

ROOT = Path(os.environ.get("ARTIFACTS", "/dados/poimtlnet"))
HERE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE / "tests/equivalence"))
sys.path.insert(0, str(ROOT / "refroot/src"))

EPOCHS = int(sys.argv[1]) if len(sys.argv) > 1 else 25
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")

graph = pickle.load(open(ROOT / "output/check2hgi/alabama/temp/checkin_graph.pt", "rb"))
P, R = int(graph["num_pois"]), int(graph["num_regions"])
features = np.asarray(graph["node_features"], dtype=np.float32)
IN = features.shape[1]

from mtlcheck.config import SubstrateConfig                                     # noqa: E402
from mtlcheck.substrate import spatial                                          # noqa: E402
from mtlcheck.substrate.model import Check2HGI as PortModel                     # noqa: E402
from mtlcheck.substrate.training import SubstrateData                           # noqa: E402

poi2vec = spatial.load_poi2vec(
    ROOT / "output/hgi/alabama/poi2vec_poi_embeddings_Alabama.csv", P, graph["placeid_to_idx"])
delaunay_index, delaunay_weight = spatial.load_delaunay(
    ROOT / "output/hgi/alabama/temp/pois.csv", ROOT / "output/hgi/alabama/temp/edges.csv",
    P, graph["placeid_to_idx"])
target = spatial.category_aggregate(features, np.asarray(graph["checkin_to_poi"]), P, 7)

tensor = lambda a, d=torch.float32: torch.tensor(np.asarray(a), dtype=d)
data = SubstrateData(
    x=tensor(features), edge_index=tensor(graph["edge_index"], torch.int64),
    edge_weight=tensor(graph["edge_weight"]),
    checkin_to_poi=tensor(graph["checkin_to_poi"], torch.int64),
    poi_to_region=tensor(graph["poi_to_region"], torch.int64),
    region_adjacency=tensor(graph["region_adjacency"], torch.int64),
    region_area=tensor(graph["region_area"]),
    coarse_region_similarity=tensor(graph["coarse_region_similarity"]),
    poi_delaunay_edge_index=delaunay_index, poi_recon_target=target).to(DEV)

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI as RefModel, corruption  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI                  # noqa: E402
from embeddings.check2hgi.model.variants import ResidualLNEncoder               # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region                       # noqa: E402
from torch_geometric.data import Data                                           # noqa: E402

ref_data = Data(x=data.x, edge_index=data.edge_index, edge_weight=data.edge_weight,
                checkin_to_poi=data.checkin_to_poi, poi_to_region=data.poi_to_region,
                region_adjacency=data.region_adjacency, region_area=data.region_area,
                coarse_region_similarity=data.coarse_region_similarity,
                num_pois=P, num_regions=R)
ref_data.poi_delaunay_edge_index = delaunay_index.to(DEV)
ref_data.poi_recon_target = target.to(DEV)

# gate=1 puts every state above the threshold, which is how the port turns the branch off.
CONFIG = SubstrateConfig(engine="traj25", epochs=EPOCHS, p2r_hard_neg_size_gate=1)

torch.manual_seed(42); np.random.seed(42)
reference = RefModel(
    hidden_channels=64,
    checkin_encoder=ResidualLNEncoder(IN, 64, num_layers=2, dropout=0.1),
    checkin2poi=Checkin2POI(64, 4), poi2region=POI2Region(64, 4),
    region2city=lambda z, a: torch.sigmoid((z.transpose(0, 1) * a).sum(dim=1)),
    corruption=corruption, alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3,
    p2r_hard_neg_min_batch=0,                       # the reference's way of turning it off
    reg_poi_mode="delaunay_gcn", num_pois=P, poi2vec_table=poi2vec, gamma_init=1.0,
    anchor_lambda=0.1, delaunay_edge_index=delaunay_index, delaunay_edge_weight=delaunay_weight,
    side_feature_dim=0, mae_poi_lambda=0.3, mae_poi_mask_rate=0.15, mae_poi_gamma=3.0,
    mae_poi_target_dim=7, mae_poi_aggr="mean", mae_poi_target_kind="category_aggregate",
    mae_poi_loss_kind="sce").to(DEV)

port = PortModel(IN, P, R, poi2vec, delaunay_index, delaunay_weight, 7, CONFIG).to(DEV)
from test_substrate_model import _transplant                                    # noqa: E402
_transplant(port, reference)


def trajectory(model, forward):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=0.0)
    torch.manual_seed(42)
    losses = []
    for _ in range(EPOCHS):
        model.train(); optimizer.zero_grad()
        loss = forward(); loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=0.9); optimizer.step()
        losses.append(float(loss.item()))
    return losses


ref_losses = trajectory(reference, lambda: reference.loss(*reference(ref_data)))
port_losses = trajectory(port, lambda: port.loss(port(data)))
deltas = [abs(a - b) for a, b in zip(ref_losses, port_losses)]
first_diff = next((i + 1 for i, d in enumerate(deltas) if d > 0), None)

out = {
    "epochs": EPOCHS, "device": str(DEV), "torch": torch.__version__,
    "in_channels": IN, "graph": "banked canonical (bidirectional, 11 channels)",
    "hard_negatives": "OFF on both sides — the port draws them vectorised, so with the branch ON "
                      "the RNG streams differ by construction",
    "params_reference": sum(p.numel() for p in reference.parameters()),
    "params_port": sum(p.numel() for p in port.parameters()),
    "reference_losses": ref_losses, "port_losses": port_losses,
    "first_epoch_that_differs": first_diff,
    "max_abs_delta": max(deltas), "final_abs_delta": deltas[-1],
}
print(json.dumps({k: v for k, v in out.items() if not k.endswith("_losses")}, indent=2))
Path(__file__).with_suffix(".json").write_text(json.dumps(out, indent=2))
