"""Adapter registry — maps adapter names to implementations."""

_adapters: dict[str, type] = {}


def register(name: str):
    """Decorator to register an adapter class."""
    def decorator(cls):
        _adapters[name] = cls
        return cls
    return decorator


def get_adapter(name: str):
    """Instantiate an adapter by name."""
    if name not in _adapters:
        raise ValueError(
            f"Unknown adapter: '{name}'. "
            f"Available: {list(_adapters.keys())}"
        )
    return _adapters[name]()


# Auto-import adapters to trigger registration
from integrations import slack_adapter, gmail_adapter, s3_adapter  # noqa: F401, E402
