"""Internal imports to work with Typing.

Farily obvious copypasta from:
https://github.com/samuelcolvin/pydantic/blob/master/pydantic/typing.py
"""

# TODO: consider future-typing to get the backport?

import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    ForwardRef,
    List,
    Mapping,
    TypeVar,
    cast,
    get_args,
    get_origin,
    get_type_hints,
)

from typing_extensions import Annotated, Literal, ParamSpec
from typingx import NoneType, isinstancex

if sys.version_info < (3, 9):

    def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:
        return type_._evaluate(globalns, localns)

else:

    def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:
        # Even though it is the right signature for python 3.9, mypy complains with
        # `error: Too many arguments for "_evaluate" of "ForwardRef"` hence the cast...
        return cast(Any, type_)._evaluate(globalns, localns, set())


if sys.version_info < (3, 9):
    # Ensure we always get all the whole `Annotated` hint, not just the annotated type.
    # For 3.7 to 3.8, `get_type_hints` doesn't recognize `typing_extensions.Annotated`,
    # so it already returns the full annotation
    get_all_type_hints = get_type_hints

else:

    def get_all_type_hints(obj: Any, globalns: Any = None, localns: Any = None) -> Any:
        return get_type_hints(obj, globalns, localns, include_extras=True)


def eval_type(x):
    from typing import _eval_type

    return _eval_type(x)
