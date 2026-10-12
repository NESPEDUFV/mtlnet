"""Model registry — select models by name from config.

Usage:
    from models.registry import register_model, create_model

    @register_model("my_model")
    class MyModel(nn.Module): ...

    model = create_model("my_model", input_dim=64, num_classes=7)

Created in Phase 4a.
"""

from torch import nn

_MODEL_REGISTRY: dict[str, type[nn.Module]] = {}
_REGISTERED = False


def register_model(name: str):
    """Decorator to register a model class under a canonical name."""
    def decorator(cls):
        if name in _MODEL_REGISTRY:
            raise ValueError(
                f"Model '{name}' already registered by {_MODEL_REGISTRY[name].__name__}; "
                f"cannot re-register with {cls.__name__}"
            )
        _MODEL_REGISTRY[name] = cls
        return cls
    return decorator


def _ensure_registered():
    """Lazily import all model modules so @register_model decorators execute."""
    global _REGISTERED
    if _REGISTERED:
        return
    import models.category  # noqa: F401
    import models.next  # noqa: F401
    import models.mtl  # noqa: F401
    _REGISTERED = True


def create_model(name: str, **kwargs) -> nn.Module:
    """Instantiate a registered model by name.

    Silently drops kwargs the target __init__ does not accept — this lets the
    same shared `model_params` dict (set up for one head, e.g. next_single)
    be reused when --model swaps in a head with a different signature
    (e.g. next_gru, which has no num_heads/seq_length).
    """
    import inspect

    _ensure_registered()
    if name not in _MODEL_REGISTRY:
        raise KeyError(
            f"Model '{name}' not registered. "
            f"Available: {sorted(_MODEL_REGISTRY.keys())}"
        )
    cls = _MODEL_REGISTRY[name]
    sig = inspect.signature(cls.__init__)
    accepts_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD
                         for p in sig.parameters.values())
    if not accepts_kwargs:
        valid = {k for k in sig.parameters if k != "self"}
        kwargs = {k: v for k, v in kwargs.items() if k in valid}
    return cls(**kwargs)


def list_models() -> list[str]:
    """Return sorted list of registered model names."""
    _ensure_registered()
    return sorted(_MODEL_REGISTRY.keys())
