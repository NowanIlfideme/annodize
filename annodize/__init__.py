"""Dataframe validation using PEP 593 (Python 3.9+) Annotated Types."""

__all__ = [
    "__version__",
    "BaseHook",
    "CompositeHook",
    "Annotated",
    "Callable",
    "P",
    "RT",
]

# TODO: Consider using typing_extensions, future-typing backports
# https://github.com/PrettyWood/future-typing

# TODO: Check out typingx, which is certain to be useful in this project
# https://github.com/PrettyWood/typingx
# just set this encoding comment at the top of your scripts: # -*- coding: future_typing -*-

from .core import RT, Annotated, BaseHook, Callable, CompositeHook, P
from .version import __version__
