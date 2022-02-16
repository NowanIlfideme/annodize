"""Field collection for namespaces (proto-classes)."""

from inspect import (
    isclass,
    isdatadescriptor,
    isfunction,
    ismemberdescriptor,
    ismethod,
    ismethoddescriptor,
)
from typing import Any, Sequence, cast

from ._field import Field

_prefield_value_checks = (
    isclass,
    isdatadescriptor,
    ismemberdescriptor,
    ismethod,
    ismethoddescriptor,
    isfunction,  # Should we allow functions?
)


def _is_prefield(name: str, value: Any) -> bool:
    """Checks whether this is a 'pre-field' object."""
    # Private
    if name.startswith("_"):
        return False
    # Special object types
    if any(chk(value) for chk in _prefield_value_checks):
        return False
    # Anything else?
    # FIXME: Improve implementation.
    return True


def get_namespace_prefields(nsp: dict[str, Any]) -> dict[str, Any]:
    """Cleans the passed namespace, returning only 'pre-fields'."""
    # TODO: Check if this implementation is correct
    res: dict[str, Any] = {}
    for name, value in nsp.items():
        if _is_prefield(name, value):
            res[name] = value
    return res


def get_namespace_annotations(nsp: dict[str, Any]) -> dict[str, Any]:
    """Gets annotations from the passed namespace."""
    # TODO: Check whether this implementation is correct
    res = dict(nsp.get("__annotations__", {}))
    assert all(isinstance(x, str) for x in res.keys())
    return cast(dict[str, Any], res)


class NamespaceFields(object):
    """A set of fields for a namespace (proto-class). All attributes are read-only.

    Attributes
    ----------
    fields : tuple[Field]
        The `Field` objects corresponding to the applicable objects of the namespace.
    """

    __slots__ = ("__fields",)

    def __init__(self, fields: Sequence[Field]):
        # Type checking
        flds = tuple(fields)
        assert all(isinstance(x, Field) for x in flds)
        # Ensure unique names
        assert len(set(x.name for x in flds)) == len(flds)
        self.__fields = flds

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        return f"{cn}({list(self.fields)!r})"

    @property
    def fields(self) -> tuple[Field, ...]:
        """The fields of this class."""
        return tuple(self.__fields)

    @classmethod
    def from_namespace(cls, namespace: dict[str, Any]) -> "NamespaceFields":
        """Gets a set of fields from a namespace (proto-class dict)."""
        anns = get_namespace_annotations(namespace)
        prefields = get_namespace_prefields(namespace)
        # Get set of keys, ordered by annotated-or-with-value
        keys: list[str] = list(anns.keys())
        keys += [x for x in prefields.keys() if x not in keys]
        # Create fields
        fields: list[Field] = [
            Field(k, anns.get(k, Any), default=prefields.get(k, Field.NoDefault))
            for k in keys
        ]
        return cls(fields)
