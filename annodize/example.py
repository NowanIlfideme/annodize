"""Example `Annode` subclass."""

from annodize.core.meta import Annode, Annotated


class Example(Annode):
    """Example class, for testing."""

    a: str
    b: Annotated[str, "bee"]
    c = "see"
    d: Annotated[str, "dee"] = "dee dee"


for k, v in Example.__fields__.items():
    print(v)

ex = Example(a="a", b="beetle")
print(ex)

ex
