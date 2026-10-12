"""Observer: time the FaithfulSTAN forward sub-components for one batch.

Pinpoints the matching-layer / self-attention bottleneck so optimization is targeted,
not guessed. Usage: PYTHONPATH=src python -m research.baselines.stan.profile_forward --state alabama
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
import numpy as np, torch

_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_root / "src"))
from configs.globals import DEVICE  # noqa: E402
from research.baselines.stan.model import FaithfulSTAN, haversine_km, _interp_scalar  # noqa: E402
from research.baselines.stan.train import load_tensors  # noqa: E402


def _t(fn, iters=10):
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    t0 = time.time()
    for _ in range(iters):
        fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return 1000.0 * (time.time() - t0) / iters  # ms/call


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--batch-size", type=int, default=2048)
    args = ap.parse_args()
    poi, hour, lat, lon, tmin, y, centroids, cat, uid, n_pois, n_regions, seq_len = load_tensors(args.state)
    B = args.batch_size
    flat_poi = poi.reshape(-1).numpy(); fl = lat.reshape(-1).numpy(); fo = lon.reshape(-1).numpy()
    v = flat_poi >= 0
    plat = np.zeros(n_pois + 1, np.float32); plon = np.zeros(n_pois + 1, np.float32)
    plat[flat_poi[v]] = fl[v]; plon[flat_poi[v]] = fo[v]
    cent = centroids.to(DEVICE)
    dd_poi = haversine_km(torch.from_numpy(plat).to(DEVICE)[:, None], torch.from_numpy(plon).to(DEVICE)[:, None],
                          cent[None, :, 0], cent[None, :, 1])
    dd_poi[n_pois].zero_()
    print(f"[{args.state}] B={B} seq_len={seq_len} n_pois={n_pois} n_regions={n_regions} "
          f"dd_poi={tuple(dd_poi.shape)} ({dd_poi.numel()*4/1e9:.2f} GB)")

    m = FaithfulSTAN(n_pois=n_pois, n_regions=n_regions, d_model=128, seq_length=seq_len).to(DEVICE)
    idx = torch.randint(0, poi.shape[0], (B,))
    poi_b = poi[idx].to(DEVICE); hour_b = hour[idx].to(DEVICE)
    lat_b = lat[idx].to(DEVICE); lon_b = lon[idx].to(DEVICE); t_b = tmin[idx].float().to(DEVICE)

    # full forward + backward
    def fwd():
        return m(poi_b, hour_b, lat_b, lon_b, t_b, dd_poi)
    print(f"  full forward:        {_t(fwd):7.1f} ms/batch")

    def fwd_bwd():
        out = m(poi_b, hour_b, lat_b, lon_b, t_b, dd_poi)
        out.sum().backward(); m.zero_grad(set_to_none=True)
    print(f"  forward+backward:    {_t(fwd_bwd, 5):7.1f} ms/batch")

    # component breakdown (mirror model.forward internals)
    pad = poi_b < 0
    poi_safe = torch.where(pad, torch.full_like(poi_b, n_pois), poi_b)
    hour_safe = torch.where(pad, torch.zeros_like(hour_b), hour_b)
    def emb():
        return m.poi_emb(poi_safe) + m.time_emb(hour_safe)
    print(f"  - input embedding:   {_t(emb):7.1f} ms")
    x = emb()
    tf = t_b.float()
    def traj_bias():
        dt = (tf.unsqueeze(2) - tf.unsqueeze(1)).abs()
        dd = haversine_km(lat_b.unsqueeze(2), lon_b.unsqueeze(2), lat_b.unsqueeze(1), lon_b.unsqueeze(1))
        return m.bias_traj(dt, dd)
    print(f"  - traj bias [B,n,n]: {_t(traj_bias):7.1f} ms")
    bias = traj_bias()
    def selfattn():
        return m.attn_traj(x, bias, pad)
    print(f"  - self-attn:         {_t(selfattn):7.1f} ms")
    S = selfattn()
    def gather_dd():
        return dd_poi[poi_safe]
    print(f"  - dd gather [B,n,R]: {_t(gather_dd):7.1f} ms")
    bias_pp = m.matching.bias_per_poi(dd_poi); bias_match = bias_pp[poi_safe]
    def matching():
        return m.matching(S, m.region_emb.weight, bias_match, pad)
    print(f"  - matching layer:    {_t(matching):7.1f} ms   <-- prime suspect")
    def interp():
        d_bin = (dd_poi.clamp(0, 200) / 200) * 63
        return _interp_scalar(m.matching.E_d_match, d_bin)
    print(f"    · interp bias:     {_t(interp):7.1f} ms")
    def einsum():
        return torch.einsum("bnd,rd->bnr", S, m.region_emb.weight)
    print(f"    · content einsum:  {_t(einsum):7.1f} ms")


if __name__ == "__main__":
    main()
