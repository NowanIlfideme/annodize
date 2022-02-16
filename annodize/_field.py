"""Field implementation."""

import warnings
from inspect import (
    Parameter,
    Signature,
    isclass,
    isdatadescriptor,
    isfunction,
    ismemberdescriptor,
    ismethod,
    ismethoddescriptor,
)
from keyword import iskeyword, issoftkeyword
from typing import (
    Annotated,
    Any,
    Callable,
    ForwardRef,
    Sequence,
    cast,
    final,
    get_args,
    get_origin,
)

TypeLike = type | ForwardRef


FIELD_REGEX = R"\R"


@final
class _NoDefault:
    """No default value is set."""


def as_field_name(x: str) -> str:
    """Checks that `x` is a valid field name, and always returns a string."""
    assert isinstance(x, str)
    x = str(x)
    assert type(x) is str
    assert not iskeyword(x)  # maybe relax this requirement? "return" would be nice...
    if issoftkeyword(x):
        # e.g. "_", "case", "match"
        warnings.warn(f"{x!r} is a soft keyword, reconsider using it.")
    assert x.isidentifier()
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
    """Represents a field. All attributes are read-only.

    Attributes
    ----------
    name : str
        The name of the field.
    type_
        The type of the field. If passed as `Annotated[type_, arg1, arg2]`,
        this field will be only the `type_` part.
    ann_args : tuple
        Annotation arguments. This is the empty tuple if not `Annotated`.
    default : NoDefault or Any
        The default value. If there's no default, we use the sentinel NoDefault.
        (This is similar to `inspect._empty`, we just use a different sentinel.)
    """

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
    """A set of fields for a function/callable. All attributes are read-only.

    Attributes
    ----------
    input_fields : tuple[Field, ...]
        The `Field` objects corresponding to the arguments.
    output_field : Field
        The `Field` corresponding to the result, with `name` set to the function's name.
    signature : Signature
        The `inspect.Signature` of the function.
    """

    __slots__ = ("__input_fields", "__output_field", "__signature")

    def __init__(
        self, input_fields: Sequence[Field], output_field: Field, signature: Signature
    ):
        # Type checking
        i_flds = tuple(input_fields)
        assert all(isinstance(x, Field) for x in i_flds)
        assert isinstance(output_field, Field)
        # Ensure unique names
        assert len(set(x.name for x in i_flds) | {output_field.name}) == len(i_flds) + 1
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
        """The function's signature."""
        return self.__signature

    @property
    def input_fields(self) -> tuple[Field, ...]:
        """The fields for the input values (arguments)."""
        return tuple(self.__input_fields)

    @property
    def output_field(self) -> Field:
        """The field for the return value, named after the function."""
        return self.__output_field

    @classmethod
    def from_callable(cls, func: Callable) -> "FunctionFields":
        """Gets a set of fields from a callable."""
        assert callable(func)
        out_name = func.__name__
        # NOTE: out_name = "return" will currently raise an exception!
        # Maybe out_name = func.__qualname__ is better, though it isn't "allowed" right now.
        sig = Signature.from_callable(func)
        input_fields = tuple(
            Field.from_inspect_parameter(param) for param in sig.parameters.values()
        )
        output_field = Field(out_name, sig.return_annotation)
        return cls(input_fields, output_field, sig)


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
            Field(k, anns.get(k, Any), default=prefields.get(k, _NoDefault))
            for k in keys
        ]
        return cls(fields)


if __name__ == "__main__":

    def func(df: str) -> Annotated[str, "schema-here"]:
        return df

    ff = FunctionFields.from_callable(func)
