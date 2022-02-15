"""Field implementation."""

import warnings
from inspect import Parameter, isclass
from keyword import iskeyword, issoftkeyword
from typing import Annotated, Any, TypeGuard, final, get_args, get_origin

_AnnType = type(Annotated[int, 1])  # is technically typing._AnnotatedAlias
TypeLike = type


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


class RawField(object):
    """Basic field definition."""

    NoDefault = _NoDefault
    __slots__ = ("__name", "__type_", "__ann_args", "__default")

    def __init__(
        self,
        name: str,
        type_: TypeLike,
        ann_args: tuple = (),
        default: Any = NoDefault,
    ):
        self.__name = as_field_name(name)
        if is_annotated(type_):
            if len(ann_args) > 0:
                raise TypeError(f"Cannot pass `ann_args` with Annotated type {type_!r}")
            type_, ann_args = split_annotation(type_)
        self.__type_ = type_
        self.__ann_args = tuple(ann_args)
        self.__default = default  # TODO: Copy this value?

    @classmethod
    def from_inspect_parameter(cls, param: Parameter) -> "RawField":
        """Creates this class from an `inspect.Parameter`."""
        if param.default is Parameter.empty:
            default = _NoDefault
        else:
            default = param.default
        return cls(param.name, param.annotation, default=default)

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
    def has_args(self) -> bool:
        """Whether this field has any annotation arguments."""
        return len(self.__ann_args) > 0

    @property
    def default(self) -> Any:
        """The default value."""
        return self.__default

    @property
    def has_default(self) -> bool:
        """Whether this field has any default value."""
        return self.__default is not _NoDefault
