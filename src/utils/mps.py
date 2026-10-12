import gc

import torch

from configs.globals import DEVICE


def clear_mps_cache():
    """Thoroughly clear device memory (MPS or CUDA) between training runs.

    Despite the name, this also handles CUDA — on Colab T4 the previous
    fold's model + optimizer + dataloader buffers stay resident in VRAM
    until Python GC fires, which can take long enough to push the next
    fold's allocations close to the 15 GB limit. Explicit gc + empty_cache
    between folds keeps memory pressure bounded.
    """
    gc.collect()
    if DEVICE.type == 'mps':
        torch.mps.empty_cache()
        if hasattr(torch.mps, 'synchronize'):
            torch.mps.synchronize()
    elif DEVICE.type == 'cuda':
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
