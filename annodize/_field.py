"""Field implementation."""

import warnings
from inspect import Parameter, isclass
from keyword import iskeyword, issoftkeyword
from typing import Annotated, Any, ForwardRef, TypeGuard, final, get_args, get_origin

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


def repr_type_aware(x: Any) -> str:
    """Clean(er) representation of the type."""
    if isinstance(x, type):
        return x.__qualname__
    else:
        return repr(x)


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
