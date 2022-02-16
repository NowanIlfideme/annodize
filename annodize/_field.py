"""Field implementation."""

import warnings
from inspect import Parameter, Signature
from keyword import iskeyword, issoftkeyword
from typing import (
    Annotated,
    Any,
    Callable,
    ForwardRef,
    Sequence,
    final,
    get_args,
    get_origin,
)

TypeLike = type | ForwardRef


@final
class _NoDefault:
    """No default value is set."""


def as_field_name(x: str) -> str:
    """Checks that `x` is a valid field name, and always returns a string."""
    assert isinstance(x, str)
    x = str(x)
    assert type(x) is str
    assert not iskeyword(x)
    if issoftkeyword(x):
        # e.g. "_", "case", "match"
        warnings.warn(f"{x!r} is a soft keyword, reconsider using it.")
    return x


def is_annotated(x: Any) -> bool:  # TypeGuard[_AnnType]:
    """Checks whether `x` is like `Annotated[type_, vals]`."""
    return get_origin(x) is Annotated


def split_annotation(ann: Any) -> tuple[TypeLike, tuple[Any, ...]]:
    """Special handling for `Annotated[type_, *args]` or just `type_`."""
    if is_annotated(ann):
        type_, *resid_args = get_args(ann)
        args = tuple(resid_args)
    else:
        type_ = ann
        args = ()
    return type_, args


def enforce_type(type_: TypeLike | str) -> TypeLike:
    """Ensures that strings are converted at least into `ForwardRef`."""
    if isinstance(type_, str):
        return ForwardRef(type_)
    return type_


# TODO: Move repr_* functions into a separate module, and have a smart function "just work"


def repr_type_aware(x: Any) -> str:
    """Clean(er) representation of the type."""
    if isinstance(x, type):
        res = x.__qualname__
        # TODO: Do we want to always add the module?...
        if hasattr(x, "__module__"):
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


@final
class Field(object):
    """Basic field definition."""

    NoDefault = _NoDefault
    __slots__ = ("__name", "__type_", "__ann_args", "__default")

    # Initializers

    def __init__(
        self,
        name: str,
        type_: TypeLike,
        ann_args: tuple = (),
        default: Any = NoDefault,
    ):
        self.__name = as_field_name(name)
        t = enforce_type(type_)
        if is_annotated(t):
            if len(ann_args) > 0:
                raise TypeError(f"Cannot pass `ann_args` with Annotated type {t!r}")
            t, ann_args = split_annotation(t)
        self.__type_ = t
        self.__ann_args = tuple(ann_args)
        self.__default = default  # TODO: Copy this value?

    @classmethod
    def from_inspect_parameter(cls, param: Parameter) -> "Field":
        """Creates this class from an `inspect.Parameter`."""
        if param.default is Parameter.empty:
            default = _NoDefault
        else:
            default = param.default
        return cls(param.name, param.annotation, default=default)

    # Read-only fields

    @property
    def name(self) -> str:
        """The name of the field."""
        return self.__name

    @property
    def type_(self) -> TypeLike:
        """Type annotation."""
        return self.__type_

    @property
    def ann_args(self) -> tuple:
        """Annotation args."""
        return tuple(self.__ann_args)

    @property
    def default(self) -> Any:
        """The default value."""
        return self.__default

    # Dunder methods

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        args: list[Any] = [self.__name, self.__type_]
        if self.has_args or self.has_default:
            args.append(self.__ann_args)
        if self.has_default:
            args.append(self.__default)
        return cn + "(" + ", ".join([repr_type_aware(x) for x in args]) + ")"

    # Helper properties

    @property
    def has_forward_ref(self) -> bool:
        """Whether the internal type is a `ForwardRef`."""
        return isinstance(self.__type_, ForwardRef)

    @property
    def has_args(self) -> bool:
        """Whether this field has any annotation arguments."""
        return len(self.__ann_args) > 0

    @property
    def has_default(self) -> bool:
        """Whether this field has any default value."""
        return self.__default is not _NoDefault

    # TODO: some way to 'finalize' ForwardRef, similar to how Pydantic does it


class FunctionFields(object):
    """A set of fields for a function/callable."""

    __slots__ = ("__input_fields", "__output_field", "__signature")

    def __init__(
        self, input_fields: Sequence[Field], output_field: Field, signature: Signature
    ):
        i_flds = tuple(input_fields)
        assert all(isinstance(x, Field) for x in i_flds)
        assert isinstance(output_field, Field)
        self.__input_fields = i_flds
        self.__output_field = output_field
        self.__signature = signature

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        xargs: list[str] = [
            repr(self.__input_fields),
            repr(self.__output_field),
            repr_sig(self.__signature),
        ]
        return cn + "(" + ", ".join(xargs) + ")"

    @property
    def signature(self) -> Signature:
        return self.__signature

    @property
    def input_fields(self) -> tuple[Field, ...]:
        return tuple(self.__input_fields)

    @property
    def output_field(self) -> Field:
        return self.__output_field

    @classmethod
    def from_callable(cls, func: Callable) -> "FunctionFields":
        """Gets a set of fields from a callable."""
        out_name = func.__name__
        # NOTE: out_name = "return" will currently raise an exception!
        sig = Signature.from_callable(func)
        input_fields = tuple(
            Field.from_inspect_parameter(param) for param in sig.parameters.values()
        )
        output_field = Field(out_name, sig.return_annotation)
        return cls(input_fields, output_field, sig)


if __name__ == "__main__":
    import pandas as pd

    def f(df: pd.DataFrame) -> Annotated[pd.DataFrame, "schema-here"]:
        return df

    ff = FunctionFields.from_callable(f)
