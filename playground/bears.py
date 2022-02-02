"""Testing out beartype.

Hey, it works without any changes. Cool. So you can use it in parallel.
"""

from typing import Annotated

import numpy as np
import pandas as pd
from beartype import beartype
from beartype.vale import Is

from annoframe.basic import Schema, check_schema

has_xz = Schema({"x": int, "z": float})

df_1 = pd.DataFrame(
    {"x": [1, 2, 3], "y": ["a", "b", "c"], "z": [10.5, np.nan, 10]},
    index=[0, 1, 2],
)


@check_schema
@beartype
def check_me(
    df: Annotated[pd.DataFrame, has_xz], x: Annotated[str, Is[lambda x: "a" in x]]
) -> bool:
    """Huh."""
    return x in df["y"]


check_me(df_1, "a")

try:
    check_me(df_1, "b")
    print("This should've errored.")
except Exception as e:
    print(e)
    print("Correctly errored.")
