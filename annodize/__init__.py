"""Dataframe validation using PEP 593 (Python 3.9+) Annotated Types."""

__all__ = [
    "__version__",
    "BaseHook",
    "CompositeHook",
    "Annotated",
    "Callable",
    "P_ORIGINAL",
    "P_HOOKED",
    "RT_ORIGINAL",
    "RT_HOOKED",
]

# TODO: Consider using typing_extensions, future-typing backports
# https://github.com/PrettyWood/future-typing

# TODO: Check out typingx, which is certain to be useful in this project
# https://github.com/PrettyWood/typingx
# just set this encoding comment at the top of your scripts: # -*- coding: future_typing -*-

from .core import (
    P_HOOKED,
    P_ORIGINAL,
    RT_HOOKED,
    RT_ORIGINAL,
    Annotated,
    BaseHook,
    Callable,
    CompositeHook,
)
from .version import __version__
