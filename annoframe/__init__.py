"""Dataframe validation using PEP 593 (Python 3.9+) Annotated Types."""

__all__ = ["Annotated", "__version__"]

# TODO: Consider using typing_extensions, future-typing backports
# https://github.com/PrettyWood/future-typing

# TODO: Check out typingx, which is certain to be useful in this project
# https://github.com/PrettyWood/typingx

from typing import Annotated

from .version import __version__
