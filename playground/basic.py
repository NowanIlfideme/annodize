"""A playground to test ideas out."""

import numpy as np
import pandas as pd

from annodize.basic import Schema, check_schema
from annodize.typing import Annotated, get_type_hints

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
