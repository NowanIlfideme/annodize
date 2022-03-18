"""Simple schemas defined by the Python stdlib `typing.TypedDict`.

Each dict field defines a single column, with the datatype given
"""


from typing import _TypedDictMeta  # type: ignore
from typing import Optional

from typing_extensions import NotRequired, Required, TypedDict

from annodize.field import NamespaceFields
from annodize.frame._schema import Schema


def as_schema(cls: type) -> Schema:
    """Function/decorator to convert the TypedDict into a Schema."""
    if not isinstance(cls, _TypedDictMeta):  # type: ignore
        raise TypeError(f"Class must be a TypedDict subclass, but got {cls!r}.")
    fields = NamespaceFields.from_namespace(cls.__dict__)
    schema = Schema.from_namespace_fields(fields)
    # FIXME: Maybe instead assign the schema to the TypedDict?
    return schema


# Testing


@as_schema
class A(TypedDict, total=False):
    """Example A."""

    x: Required[float]
    y: NotRequired[float]
    z: Optional[float]
