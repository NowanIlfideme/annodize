"""Additional stuff for inspection."""

import inspect
from typing import Any


def is_context_manager_object(cls: Any) -> bool:
    """Checks whether `cls` is a context manager object."""
    try:
        return (
            isinstance(cls, object)
            and hasattr(cls, "__enter__")
            and hasattr(cls, "__exit__")
        )
    except Exception:
        return False
