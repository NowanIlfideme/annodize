"""Extended `inspect` module."""

from inspect import (
    isabstract,
    isasyncgen,
    isasyncgenfunction,
    isawaitable,
    isbuiltin,
    isclass,
    iscode,
    iscoroutine,
    iscoroutinefunction,
    isdatadescriptor,
    isframe,
    isfunction,
    isgenerator,
    isgeneratorfunction,
    isgetsetdescriptor,
    ismemberdescriptor,
    ismethod,
    ismethoddescriptor,
    ismodule,
    isroutine,
    istraceback,
)

from typingx import is_literal, is_newtype, is_typeddict, isinstancex, issubclassx
from typingx.typing_compat import is_annotated

# More custom checks


def is_context_manager(obj) -> bool:
    """Checks whether `cls` is a context manager object."""
    try:
        return (
            isinstance(obj, object)
            and hasattr(obj, "__enter__")
            and hasattr(obj, "__exit__")
        )
    except Exception:
        return False


def is_context_manager_class(cls) -> bool:
    """Checks whether `cls` is a context manager class."""
    try:
        return (
            isinstance(cls, type)
            and hasattr(cls, "__enter__")
            and hasattr(cls, "__exit__")
        )
    except Exception:
        return False
