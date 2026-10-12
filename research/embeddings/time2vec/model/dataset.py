import numpy as np
import pandas as pd
from torch.utils.data import Dataset


class TemporalContrastiveDataset(Dataset):
    """
    Dataset for temporal contrastive learning.

    Creates positive pairs from temporally close check-ins and
    negative pairs from temporally distant check-ins.
    """

    def __init__(
        self,
        time_hours: np.ndarray,
        time_feats: np.ndarray,
        r_pos_hours: float = 1.0,
        r_neg_hours: float = 24.0,
        max_pairs: int = 2_000_000,
        k_neg_per_i: int = 5,
        max_pos_per_i: int = 20,
        seed: int = 42,
        sampling_mode: str = "feat_space",
        r_pos_feat: float = 0.03,
        r_neg_feat: float = 0.30,
        feat_cand_pool: int = 4096,
    ):
        """
        Initialize the temporal contrastive dataset.

        Args:
            time_hours: Array of absolute time in hours since first check-in
            time_feats: Array of normalized time features (hour/24, dow/7)
            r_pos_hours: Radius in hours for positive pairs (absolute_time mode)
            r_neg_hours: Minimum distance in hours for negative pairs (absolute_time mode)
            max_pairs: Maximum number of pairs to generate
            k_neg_per_i: Number of negative pairs per anchor
            max_pos_per_i: Maximum positive pairs per anchor
            seed: Random seed for reproducibility
            sampling_mode: "feat_space" (default, paper-aligned) samples pairs
                by wrap-aware distance in (hour/24, dow/7) space — resolves the
                "identical inputs labelled as negatives" issue and delivers
                +0.81 ± 0.19pp MTLnet next-task F1 over 4 seeds on Alabama.
                "absolute_time" is the legacy paper-misaligned sampler, kept
                for the 44 notebook-equivalence tests in test_time2vec.py.
                See plans/time2vec_paper_analysis.md for the full analysis.
            r_pos_feat: Positive-pair radius in feature space (feat_space mode)
            r_neg_feat: Negative-pair radius in feature space (feat_space mode)
            feat_cand_pool: Candidate pool size per anchor (feat_space mode);
                bounds per-anchor cost at O(feat_cand_pool) instead of O(N).
        """
        super().__init__()
        self.times = np.asarray(time_hours, dtype=np.float32)
        self.feats = np.asarray(time_feats, dtype=np.float32)
        self.N = len(self.times)
        self.r_pos = float(r_pos_hours)
        self.r_neg = float(r_neg_hours)
        self.sampling_mode = sampling_mode
        self.r_pos_feat = float(r_pos_feat)
        self.r_neg_feat = float(r_neg_feat)
        self.feat_cand_pool = int(feat_cand_pool)
        self.rng = np.random.default_rng(seed)

        if sampling_mode == "absolute_time":
            self.pairs = self._generate_pairs(max_pairs, k_neg_per_i, max_pos_per_i)
        elif sampling_mode == "feat_space":
            self.pairs = self._generate_pairs_feat_space(
                max_pairs, k_neg_per_i, max_pos_per_i
            )
        else:
            raise ValueError(
                f"sampling_mode must be 'absolute_time' or 'feat_space', got {sampling_mode!r}"
            )
        print(f"Total pairs generated: {len(self.pairs)} (mode={sampling_mode})")

    def _generate_pairs(self, max_pairs: int, k_neg_per_i: int, max_pos_per_i: int) -> list:
        """Generate contrastive pairs."""
        order = np.argsort(self.times)
        times_sorted = self.times[order]

        pairs_i, pairs_j, labels = [], [], []

        approx_pairs_per_i = (max_pos_per_i or 1) + k_neg_per_i
        max_i = min(self.N, max_pairs // max(1, approx_pairs_per_i) + 1)
        chosen_sorted_idx = self.rng.choice(self.N, size=max_i, replace=False)

        for idx_s in chosen_sorted_idx:
            if len(pairs_i) >= max_pairs:
                break

            i = int(order[idx_s])
            t_i = times_sorted[idx_s]

            # Positive pairs within r_pos hours
            left = np.searchsorted(times_sorted, t_i - self.r_pos, side="left")
            right = np.searchsorted(times_sorted, t_i + self.r_pos, side="right")
            cand_sorted = np.arange(left, right)
            cand_sorted = cand_sorted[cand_sorted != idx_s]

            if cand_sorted.size > 0:
                if max_pos_per_i is not None and cand_sorted.size > max_pos_per_i:
                    cand_sorted = self.rng.choice(cand_sorted, size=max_pos_per_i, replace=False)
                for s_j in cand_sorted:
                    if len(pairs_i) >= max_pairs:
                        break
                    pairs_i.append(i)
                    pairs_j.append(int(order[s_j]))
                    labels.append(1)

            if len(pairs_i) >= max_pairs:
                break

            # Negative pairs beyond r_neg hours
            got, trials, max_trials = 0, 0, 50 * k_neg_per_i
            while got < k_neg_per_i and trials < max_trials and len(pairs_i) < max_pairs:
                j = int(self.rng.integers(0, self.N))
                trials += 1
                if j != i and abs(self.times[j] - t_i) >= self.r_neg:
                    pairs_i.append(i)
                    pairs_j.append(j)
                    labels.append(0)
                    got += 1

        return list(zip(pairs_i, pairs_j, labels))

    def _generate_pairs_feat_space(
        self, max_pairs: int, k_neg_per_i: int, max_pos_per_i: int
    ) -> list:
        """Generate contrastive pairs using wrap-aware distance in (hour/24, dow/7) space.

        Resolves the structural flaw documented in plans/time2vec_paper_analysis.md
        (Deviation D6, Issue A): under the legacy absolute-time sampler, two
        check-ins with *identical* (hour, dow) but far apart in wall time would
        be labelled as negatives, forcing the model to disambiguate physically
        identical inputs.

        Cost bound: per anchor we sample at most `feat_cand_pool` random
        candidates and compute distances on that subset, so the total is
        O(N_anchors * feat_cand_pool) instead of O(N^2).
        """
        pairs_i, pairs_j, labels = [], [], []

        approx_pairs_per_i = (max_pos_per_i or 1) + k_neg_per_i
        max_i = min(self.N, max_pairs // max(1, approx_pairs_per_i) + 1)
        chosen = self.rng.choice(self.N, size=max_i, replace=False)

        cand_pool = min(self.feat_cand_pool, self.N)
        r_pos2 = self.r_pos_feat * self.r_pos_feat
        r_neg2 = self.r_neg_feat * self.r_neg_feat

        for i in chosen:
            if len(pairs_i) >= max_pairs:
                break

            # Random candidate subset (keeps O(feat_cand_pool) per anchor).
            cands = self.rng.choice(self.N, size=cand_pool, replace=False)
            cands = cands[cands != i]
            if cands.size == 0:
                continue

            dh = np.abs(self.feats[cands, 0] - self.feats[i, 0])
            dd = np.abs(self.feats[cands, 1] - self.feats[i, 1])
            # Wrap-aware circular distance on each normalized axis (period = 1).
            dh = np.minimum(dh, 1.0 - dh)
            dd = np.minimum(dd, 1.0 - dd)
            d2 = dh * dh + dd * dd

            pos_mask = d2 <= r_pos2
            neg_mask = d2 >= r_neg2

            pos_cands = cands[pos_mask]
            if pos_cands.size > 0:
                if max_pos_per_i is not None and pos_cands.size > max_pos_per_i:
                    pos_cands = self.rng.choice(pos_cands, size=max_pos_per_i, replace=False)
                for j in pos_cands:
                    if len(pairs_i) >= max_pairs:
                        break
                    pairs_i.append(int(i))
                    pairs_j.append(int(j))
                    labels.append(1)

            if len(pairs_i) >= max_pairs:
                break

            neg_cands = cands[neg_mask]
            if neg_cands.size > 0:
                take = min(k_neg_per_i, neg_cands.size)
                neg_chosen = self.rng.choice(neg_cands, size=take, replace=False)
                for j in neg_chosen:
                    if len(pairs_i) >= max_pairs:
                        break
                    pairs_i.append(int(i))
                    pairs_j.append(int(j))
                    labels.append(0)

        return list(zip(pairs_i, pairs_j, labels))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        i, j, label = self.pairs[idx]
        return self.feats[i], self.feats[j], label

    @staticmethod
    def from_checkins(checkins: pd.DataFrame, **kwargs) -> 'TemporalContrastiveDataset':
        """
        Create dataset directly from check-ins DataFrame.

        Args:
            checkins: DataFrame with 'local_datetime' column
            **kwargs: Additional arguments for TemporalContrastiveDataset

        Returns:
            TemporalContrastiveDataset instance
        """
        time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(checkins)
        return TemporalContrastiveDataset(time_hours=time_hours, time_feats=time_feats, **kwargs)

    @staticmethod
    def extract_time_features(checkins: pd.DataFrame) -> tuple:
        """
        Extract temporal features from check-ins.

        Args:
            checkins: DataFrame with 'local_datetime' column

        Returns:
            Tuple of (time_hours, time_feats)
        """
        if "local_datetime" not in checkins.columns:
            raise ValueError("Required column 'local_datetime' missing")

        dt = pd.to_datetime(checkins["local_datetime"].astype(str), utc=True, errors="coerce")
        valid_mask = dt.notna()

        if not valid_mask.all():
            print(f"Warning: {(~valid_mask).sum()} invalid datetime entries will be dropped")

        dt = dt[valid_mask]

        # Absolute time in hours
        t0 = dt.min()
        time_hours = (dt - t0).dt.total_seconds() / 3600.0

        # Normalized features: hour/24 and day_of_week/7
        hour = dt.dt.hour + dt.dt.minute / 60.0
        dow = dt.dt.weekday

        time_feats = np.stack([
            (hour / 24.0).astype(np.float32),
            (dow / 7.0).astype(np.float32)
        ], axis=1)

        return time_hours.values, time_feats