"""Utilities to work with Typing."""

# TODO: consider future-typing to get the backport?

from typing import (
    Annotated,
    Any,
    Callable,
    ForwardRef,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

try:
    from typing import ParamSpec, TypeAlias  # type: ignore

except ImportError:
    from typing_extensions import ParamSpec, TypeAlias  # type: ignore

from typingx import isinstancex
