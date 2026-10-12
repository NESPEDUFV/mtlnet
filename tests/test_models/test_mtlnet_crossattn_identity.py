"""F52 — identity_cross_attn probe tests.

Pin the contract for the new ``identity_cross_attn=True`` flag:
- The block's cross-attention output is replaced with zero
  (so a + a_upd reduces to a, then ln_a1 + FFN run on a alone).
- LayerNorms and per-task FFNs still execute → P5 (identity-crossattn) is
  STRICTLY between P1 (no_crossattn at all) and H3-alt (full cross-attn) in
  the ablation hierarchy.
- Mutually exclusive with disable_cross_attn.
"""

import pytest
import torch

from models.mtl import MTLnetCrossAttn
from models.mtl.mtlnet_crossattn.model import _CrossAttnBlock


class TestIdentityCrossAttnBlock:
    """Direct test of the _CrossAttnBlock contract under identity_attn."""

    def test_identity_attn_zeroes_cross_contribution(self):
        torch.manual_seed(0)
        B, T, D = 2, 4, 16
        block_ref = _CrossAttnBlock(dim=D, num_heads=4, ffn_dim=D, dropout=0.0)
        block_id = _CrossAttnBlock(
            dim=D, num_heads=4, ffn_dim=D, dropout=0.0, identity_attn=True,
        )
        # Copy weights so FFN+LN are bit-identical.
        block_id.load_state_dict(block_ref.state_dict())
        block_ref.eval()
        block_id.eval()

        a = torch.randn(B, T, D)
        b = torch.randn(B, T, D)

        with torch.no_grad():
            a_ref, b_ref = block_ref(a, b)
            a_id, b_id = block_id(a, b)

        # Without cross-attn mixing, identity_attn output depends on `a`
        # alone (and `b` alone) — so swapping `b` cannot change `a_id`.
        b2 = torch.randn(B, T, D)
        with torch.no_grad():
            a_id2, _ = block_id(a, b2)
        assert torch.allclose(a_id, a_id2, atol=1e-6), (
            "identity_attn should make stream a's output independent of b"
        )
        # Reference (full cross-attn) WILL change when b changes.
        with torch.no_grad():
            a_ref2, _ = block_ref(a, b2)
        assert not torch.allclose(a_ref, a_ref2, atol=1e-6), (
            "Full cross-attn must show b-dependence — sanity guard"
        )

    def test_identity_attn_preserves_ffn_path(self):
        """The FFN-only stream `a → ln_a1(a) → +ffn_a → ln_a2` must produce a
        non-trivial transformation of `a` (so we know FFN+LN didn't get
        accidentally short-circuited too)."""
        torch.manual_seed(1)
        B, T, D = 2, 4, 16
        block_id = _CrossAttnBlock(
            dim=D, num_heads=4, ffn_dim=D, dropout=0.0, identity_attn=True,
        )
        block_id.eval()
        a = torch.randn(B, T, D)
        b = torch.randn(B, T, D)
        with torch.no_grad():
            a_out, _ = block_id(a, b)
        assert a_out.shape == a.shape
        assert not torch.allclose(a_out, a, atol=1e-4), (
            "FFN+LN must still transform the stream — got identity output"
        )


class TestMTLnetCrossAttnIdentityFlag:
    """End-to-end: the model-level flag wires through to every block."""

    def _make(self, **kwargs):
        torch.manual_seed(42)
        return MTLnetCrossAttn(
            feature_size=64,
            shared_layer_size=128,
            num_classes=7,
            num_heads=4,
            num_layers=2,
            seq_length=4,
            num_shared_layers=2,
            num_crossattn_blocks=2,
            num_crossattn_heads=4,
            **kwargs,
        )

    def test_flag_propagates_to_blocks(self):
        m = self._make(identity_cross_attn=True)
        for block in m.crossattn_blocks:
            assert block.identity_attn is True
        m_default = self._make()
        for block in m_default.crossattn_blocks:
            assert block.identity_attn is False

    def test_disable_and_identity_mutually_exclusive(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            self._make(disable_cross_attn=True, identity_cross_attn=True)

    def test_identity_forward_b_independent(self):
        """Swap the b stream — under identity_cross_attn, the cat output must
        not change (since cat sees no b influence). Eval mode to silence
        dropout. Legacy MTLnet's cat head expects flat (B, D) input.
        """
        m = self._make(identity_cross_attn=True).eval()
        B, T, D = 2, 4, 64
        cat_in = torch.randn(B, D)
        next_in1 = torch.randn(B, T, D)
        next_in2 = torch.randn(B, T, D)
        with torch.no_grad():
            cat_out_1, _ = m((cat_in, next_in1))
            cat_out_2, _ = m((cat_in, next_in2))
        assert torch.allclose(cat_out_1, cat_out_2, atol=1e-5)
