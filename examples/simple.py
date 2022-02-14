"""Simple example."""

import pandas as pd

from annodize.core.wrapper import AnnodizeWrapper
from annodize.ext.typing import Annotated

DO_RUNTIME_CHECK = False

if DO_RUNTIME_CHECK:
    wrap = AnnodizeWrapper()  # no-op wrapper
else:
    wrap = AnnodizeWrapper()  # TODO: add something here


@wrap
def foo(
    x: Annotated[pd.DataFrame, "foo"], val: int | float = 3
) -> Annotated[pd.DataFrame, "bar"]:
    """Example function that is wrapped."""
    return x.assign(**{"bar": x["foo"] * val})


df = pd.DataFrame({"foo": [1, 2, 3]})
res = foo(df)
res
