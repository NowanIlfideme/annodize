"""A playground to test ideas out."""

import numpy as np
import pandas as pd

from annoframe.typing import *


class Schema(object):
    """TODO: Figure out a flexible, extensible schema.

    Consider the following Schema definition methods:

    1. Similar to Pydantic (class attributes), but with our own semantics
    2. With instances rather than classes (for super simple cases?)
    3. Using Pydantic models directly (validating each row w/ dtype conversion?)

    We can support all of them at once, in theory... or as extensions.
    """

    def __init__(self, *args, **kwargs):
        self._args = args
        self._kwargs = kwargs

    @property
    def args(self) -> tuple:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any]:
        return dict(self._kwargs)

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        argstr = ", ".join(
            [repr(v) for v in self._args]
            + [f"{k}={v!r}" for k, v in self._kwargs.items()]
        )
        return f"{cn}({argstr})"


P = ParamSpec("P")
T = TypeVar("T")


def check_schema(f: Callable[P, T]) -> Callable[P, T]:
    """Decorator to check the schema.

    TODO: Implement wrapping, validation on/off switch, other options.
    We can be inspired by Pydantic's validation checker.
    And we can even use Pydantic to check non-DF types, if we want!
    """
    return f


has_xz = Schema({"x": int, "z": float})

df_1 = pd.DataFrame(
    {"x": [1, 2, 3], "y": ["a", "b", "c"], "z": [10.5, np.nan, 10]},
    index=[0, 1, 2],
)


@check_schema
def func(df: Annotated[pd.DataFrame, has_xz]) -> Annotated[pd.DataFrame, Schema("bar")]:
    """Example function."""
    return df


hints = get_type_hints(func, include_extras=True)

func(df_1)
