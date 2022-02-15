"""Miscellaneous utility functions and types."""

import warnings
from keyword import iskeyword, issoftkeyword

from annodize.ext.inspect import is_annotated
from annodize.ext.typing import (
    Annotated,
    Any,
    Callable,
    Generator,
    Optional,
    Sequence,
    Tuple,
    get_args,
    get_origin,
    no_type_check,
)


def as_field_name(x: str) -> str:
    """Checks that `x` is a valid field name, and always returns a string."""
    assert isinstance(x, str)
    x = str(x)
    assert type(x) is str
    assert not iskeyword(x)
    if issoftkeyword(x):
        # e.g. "_", "case", "match"
        warnings.warn(f"{x!r} is a soft keyword, reconsider using it.")
    return x


def split_annotation(ann: Any) -> tuple[type, tuple[Any, ...]]:
    """Special handling for `Annotated[type_, *args]` or just `type_`."""
    if is_annotated(ann):
        type_, *resid_args = get_args(ann)
        args = tuple(resid_args)
    else:
        type_ = ann
        args = ()
    # FIXME: Ensure that `type_` is actually a type!
    return type_, args


@no_type_check
def create_annotation(base_type: type, *args: Any) -> Annotated:
    """Creates an annotation."""
    if len(args) == 0:
        raise TypeError("At least one argument must be specified!")
    return _recurse_ann(base_type, *args)


@no_type_check
def _recurse_ann(base: Any, arg0: Any, *xargs: Any) -> Annotated:
    """Recursive annotation-adding function."""
    if len(xargs) == 0:
        return Annotated[base, arg0]
    bt = Annotated[base, arg0]
    return _recurse_ann(bt, *xargs)


def clean_repr_type(type_: type) -> str:
    """Clean(er) representation of the type."""
    if isinstance(type_, type):
        return type_.__qualname__
    else:
        return repr(type_)


def is_private(name: str) -> bool:
    return name.startswith("_")
