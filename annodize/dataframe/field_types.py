"""Defining field types."""

from typing import Annotated, TypeVar, no_type_check

K = TypeVar("K")


class Nullable:
    """A field marked as nullable."""

    @no_type_check
    def __class_getitem__(self, typ: type[K], *others) -> Annotated[K, "Nullable"]:
        """Shortcut for `Annotated[typ, Nullable, *others]`."""
        return Annotated[(typ, Nullable, *others)]
