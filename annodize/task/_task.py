"""Task definition."""

from typing import Annotated, Callable, List

import networkx as nx
from makefun import partial

from annodize.field import FunctionFields


class Task(object):
    """Defines a tasks with inputs and outputs."""


class Artifact(object):
    """Defines an artifact."""


class TaskGraph(object):
    """Task graph manager."""

    def __init__(self, graph: nx.DiGraph = None):
        if graph is None:
            graph = nx.DiGraph()
        else:
            # TODO: Check graph
            pass
        self.__graph = graph

    @property
    def graph(self) -> nx.DiGraph:
        # return self.__graph.copy(as_view=True)  # or not view?
        return self.__graph

    def task(self, f: Callable | str):
        """Registers a function as a task."""
        if callable(f):
            return self.__register(f)
        elif isinstance(f, str):
            return partial(self.__register, name=f)
        raise TypeError(f"Expected callable or str, got {f!r}")

    def __register(self, func: Callable, name: str = None):
        flds = FunctionFields.from_callable(func)
        if name is None:
            name = f"{func.__module__}.{func.__qualname__}"
        g = self.__graph

        g.edges
        for fld_in in flds.input_fields:
            pass
        fld_out = flds.output_field
        return func


if __name__ == "__main__":
    from typing import Annotated

    import pandas as pd
    from pydantic_yaml import YamlModel

    class MyConfig(YamlModel):
        col: str
        val: float = 0.0

    mgr = TaskGraph()

    @mgr.task
    def func(df: pd.DataFrame, cfg: MyConfig) -> pd.DataFrame:
        """My custom function."""
        return df.assign(**{cfg.col: cfg.val})
