"""Design L (Lever 5) — Design B + distribution-level KL distillation to POI2Vec.

Same architecture as Design B (frozen Linear(POI2Vec) residual injected at
the POI-pool boundary, cat path detached). Replaces Design M's *pointwise*
cosine alignment with a *distribution-level* KL on the top-k neighbour
similarity softmax:

    S_merge[i, :] = top-k cosine(merge_poi_emb[i], merge_poi_emb[other])
    S_p2v[i, :]   = top-k cosine(POI2Vec[i],       POI2Vec[other])         # precomputed
    L_distill     = KL( softmax(S_merge / tau) || softmax(S_p2v / tau) ).mean()

The neighbour set per POI is FIXED — chosen once from the POI2Vec teacher
geometry — so per-step cost is O(N · k). Compatible with the
``startswith("check2hgi_design_")`` branch in
``scripts/p1_region_head_ablation.py`` because the output directory uses the
``check2hgi_design_l`` prefix.

Loss boundaries (identical to Design M except for the distill term)::

    L_total = L_c2hgi  +  lambda_d * L_distill_topkKL

Outputs to ``output/check2hgi_design_l/<state>/``:
  - embeddings.parquet       (per-check-in, from canonical encoder — cat-grade)
  - poi_embeddings.parquet   (per-POI from poi_emb_for_reg — ranking-aware)
  - region_embeddings.parquet (reg-grade)

Usage::

    python scripts/probe/build_design_l_distkl.py --state alabama --epochs 500 \
        --distill-lambda 0.1 --distill-k 16 --distill-tau 1.0
"""
from __future__ import annotations
import argparse, math, pickle, sys
from pathlib import Path
import numpy as np, pandas as pd, torch, torch.nn as nn, torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
from embeddings.hgi.model.RegionEncoder import POI2Region

POI2VEC_DIM = 64


def _build_topk_neighbours(poi2vec_table: torch.Tensor, k: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Pick top-k neighbours per POI using POI2Vec cosine similarity (excludes self).

    Returns
    -------
    nbr_idx : LongTensor[N, k]
        Indices of top-k POI2Vec-nearest neighbours per POI.
    teacher_logits : FloatTensor[N, k]
        Cosine similarity scores of those neighbours (pre-temperature, pre-softmax).
    """
    t = F.normalize(poi2vec_table.float(), dim=-1)
    N = t.shape[0]
    # full NxN cosine; OK at N ~ 10k-50k on CPU — same scale as Design M's distill.
    sim = t @ t.t()
    sim.fill_diagonal_(-float("inf"))  # exclude self
    teacher_logits, nbr_idx = sim.topk(k=k, dim=-1)
    return nbr_idx, teacher_logits


class Check2HGI_DesignL(Check2HGI):
    def __init__(
        self,
        *args,
        poi2vec_table: torch.Tensor,
        nbr_idx: torch.Tensor,
        teacher_logits: torch.Tensor,
        tau: float = 1.0,
        gamma_init: float = 1.0,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        D = self.hidden_channels
        self.poi2vec_proj = nn.Linear(POI2VEC_DIM, D, bias=True)
        self.gamma = nn.Parameter(torch.tensor(float(gamma_init)))
        self.tau = float(tau)
        self.register_buffer("poi2vec_table", poi2vec_table.float())
        # neighbour bookkeeping (fixed across training)
        self.register_buffer("nbr_idx", nbr_idx.long())                  # [N, k]
        self.register_buffer("teacher_logits", teacher_logits.float())   # [N, k]

    def forward(self, data):
        num_pois = data.num_pois; num_regions = data.num_regions

        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(cor_x, data.edge_index, data.edge_weight)

        pos_poi_emb_canonical = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)
        neg_poi_emb_canonical = self.checkin2poi(neg_checkin_emb, data.checkin_to_poi, num_pois)

        residual = self.poi2vec_proj(self.poi2vec_table)
        pos_poi_emb_for_reg = pos_poi_emb_canonical.detach() + self.gamma * residual
        neg_poi_emb_for_reg = neg_poi_emb_canonical.detach() + self.gamma * residual

        pos_region_emb = self.poi2region(pos_poi_emb_for_reg, data.poi_to_region, data.region_adjacency)
        neg_region_emb = self.poi2region(neg_poi_emb_for_reg, data.poi_to_region, data.region_adjacency)
        city_emb = self.region2city(pos_region_emb, data.region_area)

        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb_for_reg
        self.region_embedding = pos_region_emb

        pos_poi_expanded = pos_poi_emb_canonical[data.checkin_to_poi]
        neg_poi_indices = self._sample_negative_indices(data.checkin_to_poi, num_pois, data.x.device)
        neg_poi_expanded = pos_poi_emb_canonical[neg_poi_indices]
        pos_region_expanded = pos_region_emb[data.poi_to_region]
        neg_region_indices = self._sample_negative_indices_with_similarity(
            data.poi_to_region, num_regions, data.coarse_region_similarity, data.x.device)
        neg_region_expanded = pos_region_emb[neg_region_indices]

        return (
            pos_checkin_emb, pos_poi_expanded, neg_poi_expanded,
            pos_poi_emb_for_reg, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb,
        )

    def distill_loss(self) -> torch.Tensor:
        """KL( softmax(S_student / tau) || softmax(S_teacher / tau) ).

        Student similarity S_merge is computed on ``self.poi_embedding`` (the
        merged POI emb used by the reg path) over the FIXED neighbour set
        ``nbr_idx`` per POI.
        """
        # TODO(Lever 5): the spec is ambiguous on KL direction. We use
        # KL(student || teacher) (student is the predicted/log-probs side),
        # which is standard "match the teacher" distillation. Flip the
        # arguments below if a teacher-forced reverse-KL is preferred.
        student = F.normalize(self.poi_embedding, dim=-1)          # [N, D]
        # gather neighbours: rows are POIs, cols are k-neighbour student vecs.
        nbr_student = student[self.nbr_idx]                        # [N, k, D]
        # similarity = cos(student[i], student[nbr_idx[i, j]])
        student_logits = (nbr_student * student.unsqueeze(1)).sum(dim=-1)  # [N, k]

        log_p_student = F.log_softmax(student_logits / self.tau, dim=-1)
        p_teacher = F.softmax(self.teacher_logits / self.tau, dim=-1)
        # KL(student || teacher) = sum_j p_student * (log p_student - log p_teacher)
        # Equivalent to F.kl_div with log-target form. Use batchmean over POIs.
        return F.kl_div(
            log_p_student,
            p_teacher,
            reduction="batchmean",
        )


def load_poi2vec(state, num_pois, placeid_to_idx):
    state_lc = state.lower(); state_cap = state.capitalize()
    csv = REPO / f"output/hgi/{state_lc}/poi2vec_poi_embeddings_{state_cap}.csv"
    df = pd.read_csv(csv)
    emb_cols = [str(i) for i in range(POI2VEC_DIM)]
    arr = np.zeros((num_pois, POI2VEC_DIM), dtype=np.float32)
    for placeid, vec in zip(df["placeid"].astype(int).tolist(), df[emb_cols].to_numpy(np.float32)):
        idx = placeid_to_idx.get(placeid)
        if idx is not None:
            arr[idx] = vec
    return torch.from_numpy(arr)


def train(state, args):
    state_lc = state.lower()
    out_dir = REPO / "output" / "check2hgi_design_l" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_pois = d["num_pois"]; num_regions = d["num_regions"]
    print(
        f"[{state_lc}] pois={num_pois} regions={num_regions} feat={in_channels} "
        f"lambda_d={args.distill_lambda} k={args.distill_k} tau={args.distill_tau}"
    )

    device = torch.device(args.device)
    poi2vec = load_poi2vec(state, num_pois, d["placeid_to_idx"])
    nbr_idx, teacher_logits = _build_topk_neighbours(poi2vec, k=args.distill_k)

    data = Data(
        x=torch.tensor(d["node_features"], dtype=torch.float32),
        edge_index=torch.tensor(d["edge_index"], dtype=torch.int64),
        edge_weight=torch.tensor(d["edge_weight"], dtype=torch.float32),
        checkin_to_poi=torch.tensor(d["checkin_to_poi"], dtype=torch.int64),
        poi_to_region=torch.tensor(d["poi_to_region"], dtype=torch.int64),
        region_adjacency=torch.tensor(d["region_adjacency"], dtype=torch.int64),
        region_area=torch.tensor(d["region_area"], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(d["coarse_region_similarity"], dtype=torch.float32),
        num_pois=num_pois, num_regions=num_regions,
    ).to(device)
    metadata = d["metadata"]

    checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
    checkin2poi = Checkin2POI(args.dim, args.attention_head)
    poi2region = POI2Region(args.dim, args.attention_head)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI_DesignL(
        hidden_channels=args.dim, checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi, poi2region=poi2region,
        region2city=region2city, corruption=corruption,
        alpha_c2p=args.alpha_c2p, alpha_p2r=args.alpha_p2r, alpha_r2c=args.alpha_r2c,
        poi2vec_table=poi2vec, nbr_idx=nbr_idx, teacher_logits=teacher_logits,
        tau=args.distill_tau, gamma_init=args.gamma_init,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma) if args.gamma != 1.0 else None

    t = trange(1, args.epochs + 1, desc=f"Train L[{state_lc}]")
    lowest = math.inf; best_epoch = 0; best_state = None
    POSTFIX_EVERY = 25
    for epoch in t:
        model.train(); optimizer.zero_grad()
        outputs = model(data)
        loss_main = model.loss(*outputs)
        loss_distill = model.distill_loss()
        loss = loss_main + args.distill_lambda * loss_distill
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        l = loss.item()
        if l < lowest:
            lowest = l; best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch % POSTFIX_EVERY == 0 or epoch == args.epochs:
            t.set_postfix(loss=f"{l:.4f}", kl=f"{loss_distill.item():.4f}", best_ep=best_epoch, refresh=False)
            t.refresh()

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f}")
    model.load_state_dict(best_state); model.eval()
    with torch.no_grad():
        _ = model(data)
        checkin_emb, poi_emb, region_emb = model.get_embeddings()

    emb_np = checkin_emb.numpy()
    df = pd.DataFrame(emb_np, columns=[f"{i}" for i in range(emb_np.shape[1])])
    df.insert(0, "datetime", metadata["datetime"].values)
    df.insert(0, "category", metadata["category"].values)
    df.insert(0, "placeid", metadata["placeid"].values)
    df.insert(0, "userid", metadata["userid"].values)
    df.to_parquet(out_dir / "embeddings.parquet", index=False)

    poi_np = poi_emb.numpy()
    poi_df = pd.DataFrame(poi_np, columns=[f"{i}" for i in range(poi_np.shape[1])])
    placeid_to_idx = d["placeid_to_idx"]
    idx_to_placeid = {v: k for k, v in placeid_to_idx.items()}
    poi_df.insert(0, "placeid", [idx_to_placeid.get(i, i) for i in range(len(poi_df))])
    poi_df.to_parquet(out_dir / "poi_embeddings.parquet", index=False)

    reg_np = region_emb.numpy()
    reg_df = pd.DataFrame(reg_np, columns=[f"reg_{i}" for i in range(reg_np.shape[1])])
    reg_df.insert(0, "region_id", range(num_regions))
    reg_df.to_parquet(out_dir / "region_embeddings.parquet", index=False)

    (out_dir / "temp").mkdir(exist_ok=True)
    import shutil
    shutil.copy(graph_path, out_dir / "temp" / "checkin_graph.pt")
    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")
    print(f"[{state_lc}] wrote {out_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--num-layers", dest="num_layers", type=int, default=2)
    ap.add_argument("--attention-head", dest="attention_head", type=int, default=4)
    ap.add_argument("--alpha-c2p", dest="alpha_c2p", type=float, default=0.4)
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.3)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--gamma-init", dest="gamma_init", type=float, default=1.0)
    ap.add_argument("--distill-lambda", dest="distill_lambda", type=float, default=0.1,
                    help="Weight on the KL distill term (Design M default: 0.1).")
    ap.add_argument("--distill-k", dest="distill_k", type=int, default=16,
                    help="Top-k POI2Vec neighbours per POI (spec: 10-20).")
    ap.add_argument("--distill-tau", dest="distill_tau", type=float, default=1.0,
                    help="Softmax temperature (spec: ~1.0; keep > 0.5).")
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()
    train(args.state, args)


if __name__ == "__main__":
    main()
