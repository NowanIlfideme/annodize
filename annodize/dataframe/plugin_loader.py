"""Loads `annodize.dataframe` plugins."""

import importlib.metadata as _im
import warnings
from typing import Callable


def load_plugins():
    """Loads all plugins."""
    eps: _im.EntryPoints = _im.entry_points(group="annodize.dataframe")
    for ep_i in eps:
        try:
            func: Callable = ep_i.load()
            func()
        except Exception:
            warnings.warn(f"Failed to load plugin for: {ep_i.name!r}")


if __name__ == "__main__":
    load_plugins()
