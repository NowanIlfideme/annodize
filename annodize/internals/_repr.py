"""Function helpers for string representation."""

# TODO: Make a smart function that "just works"

from inspect import Parameter, Signature
from typing import Any


def repr_type_aware(x: Any) -> str:
    """Clean(er) representation of the type."""
    if isinstance(x, type):
        res = x.__qualname__
        # TODO: Do we want to always add the module?...
        if False and hasattr(x, "__module__"):
            res = x.__module__ + "." + res
        return res
    else:
        return repr(x)


def repr_sig(x: Signature | Parameter) -> str:
    """Proper repr for a Signature or Parameter."""
    cn = type(x).__qualname__
    parts: list[str] = []
    if isinstance(x, Signature):
        if len(x.parameters) > 0:
            par_reprs = [repr_sig(p) for p in x.parameters.values()]
            parts.append("[" + ", ".join(par_reprs) + "]")
        if x.return_annotation is not x.empty:
            parts.append("return_annotation=" + repr_type_aware(x.return_annotation))
    elif isinstance(x, Parameter):
        parts.append(repr(x.name))
        kind_name = [k for k, v in Parameter.__dict__.items() if v == x.kind][0]
        parts.append(f"Parameter.{kind_name}")
        if x.default is not x.empty:
            parts.append("default=" + repr_type_aware(x.default))
        if x.annotation is not x.empty:
            parts.append("annotation=" + repr_type_aware(x.annotation))
    else:
        raise TypeError(f"Bad type {type(x)} passed: {x!r}")
    return f"{cn}({', '.join(parts)})"
