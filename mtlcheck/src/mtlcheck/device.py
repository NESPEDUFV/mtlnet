"""Device and precision — resolved once, declared never inferred.

Two rules this module exists to enforce:

1. **One model, three devices.** CUDA, MPS and CPU run the same code. The only device-conditional
   behaviour here is where the platform genuinely cannot do the thing (see `MPS_RANK_ELEMENT_LIMIT`).
2. **Precision is declared.** The old trainer decided precision from the state's region cardinality
   (`_auto_fp32_for_large_c`), so a bare run was fp16 at Alabama and fp32 at California. Here the
   precision comes from the config or the run does not start.
"""

from __future__ import annotations

import contextlib
import logging
from dataclasses import dataclass
from enum import Enum

import torch

logger = logging.getLogger(__name__)

# MPSGraph refuses tensors with more than INT_MAX elements. The rank-of-target computation is
# [N, C], which crosses it on a large state (California train fold: 286K x 8497 = 2.4e9). Above
# this the rank falls back to CPU — a platform limit, not a choice.
MPS_RANK_ELEMENT_LIMIT = 2 ** 31


class Precision(str, Enum):
    FP32 = "fp32"
    BF16 = "bf16"
    FP16 = "fp16"


@dataclass(frozen=True)
class DeviceSpec:
    """Everything the rest of the code needs to know about where it is running."""

    device: torch.device
    precision: Precision
    can_compile: bool
    can_tf32: bool
    #: Botões que a receita pediu e este device não honra — vão para `warnings` do artefato.
    unhonoured: tuple[str, ...] = ()

    @property
    def type(self) -> str:
        return self.device.type

    def autocast(self):
        """The training/eval autocast context for this spec.

        fp16 without a GradScaler overflows the 65504 ceiling on wide region logits and produces a
        deterministic NaN around epoch 30 that poisons the shared backbone — the documented cause of
        the voided California and Texas cells. It is reachable only by asking for it explicitly, and
        it warns when you do.
        """
        if self.device.type != "cuda" or self.precision is Precision.FP32:
            return contextlib.nullcontext()
        if self.precision is Precision.FP16:
            logger.warning(
                "fp16 autocast requested: this trainer has no GradScaler, and fp16 overflowed the "
                "65504 ceiling on wide region logits in the reference implementation (voided CA/TX "
                "cells). Use fp32 unless you are deliberately reproducing that regime."
            )
        dtype = torch.bfloat16 if self.precision is Precision.BF16 else torch.float16
        return torch.autocast("cuda", dtype=dtype)


def resolve(precision: Precision, *, prefer: str | None = None,
            compile_requested: bool = False, tf32_requested: bool = False) -> DeviceSpec:
    """Pick the device and validate the requested precision against it.

    `prefer` forces a device ("cuda" / "mps" / "cpu") for tests and for pinning a machine; the
    default order is CUDA -> MPS -> CPU.
    """
    device = torch.device(prefer) if prefer else _auto_device()

    if device.type != "cuda" and precision is not Precision.FP32:
        # Not a silent downgrade: a run that asked for bf16 and got fp32 is a different run, and the
        # provenance record would be a lie.
        raise ValueError(
            f"precision={precision.value} is only available on CUDA; this process resolved to "
            f"{device.type}. Ask for fp32, or run where the requested precision exists."
        )

    can_compile = compile_requested and device.type == "cuda"
    if compile_requested and not can_compile:
        logger.info("--compile ignored on %s (torch.compile is CUDA-only here)", device.type)

    can_tf32 = tf32_requested and device.type == "cuda"
    if can_tf32:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    # O mesmo argumento que faz a precisão levantar acima: uma execução que pediu compile e não o
    # teve é outra execução. Ela não levanta porque compile e tf32 não mudam a especificação
    # matemática do modelo -- mas o `science_fingerprint` grava `compile = true` de qualquer jeito,
    # então sem este registro o artefato afirma um botão que o run não usou, e o único vestígio é
    # uma linha de log.
    unhonoured = tuple(
        f"{nome} declarado na receita e ignorado em {device.type}"
        for nome, pedido, obtido in (("compile", compile_requested, can_compile),
                                     ("tf32", tf32_requested, can_tf32))
        if pedido and not obtido)

    return DeviceSpec(device=device, precision=precision,
                      can_compile=can_compile, can_tf32=can_tf32, unhonoured=unhonoured)


def _auto_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def empty_cache(device: torch.device) -> None:
    """Release cached allocations between folds. A no-op where it does not apply."""
    if device.type == "cuda":
        torch.cuda.empty_cache()
    elif device.type == "mps":
        torch.mps.empty_cache()


def describe(spec: DeviceSpec) -> str:
    """One line for the run log and the provenance record."""
    name = ""
    if spec.device.type == "cuda":
        name = f" ({torch.cuda.get_device_name(0)})"
    bits = [spec.device.type + name, spec.precision.value]
    if spec.can_compile:
        bits.append("compile")
    if spec.can_tf32:
        bits.append("tf32")
    return " · ".join(bits) + f" · torch {torch.__version__}"


__all__ = ["Precision", "DeviceSpec", "resolve", "empty_cache", "describe",
           "MPS_RANK_ELEMENT_LIMIT"]
