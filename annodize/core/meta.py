"""F.

NOTE
----
mypy dies on annotations that are literally `Annotated` (without args), so...
"""

from abc import ABCMeta
from types import FunctionType
from typing import TYPE_CHECKING

from annodize.ext.typing import (
    Any,
    ClassVar,
    eval_type,
    final,
    get_type_hints,
    no_type_check,
)

from .misc import (
    as_field_name,
    clean_repr_type,
    create_annotation,
    is_private,
    split_annotation,
)

if TYPE_CHECKING:
    from typing import Annotated
else:
    from annodize.ext.typing import Annotated


NoDefault = Ellipsis


@final
class Field(object):
    """Structured field for annotated."""

    __slots__ = ("__name", "__base_type", "__anno_args", "__default")

    def __init__(
        self, name: str, base_type: type, anno_args: tuple, *, default: Any = NoDefault
    ):
        self.__name = as_field_name(name)
        self.__base_type = base_type
        self.__anno_args = anno_args
        self.__default = default  # FIXME: copy?

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        args = [repr(self.name), clean_repr_type(self.base_type), repr(self.anno_args)]
        if self.default is not NoDefault:
            args.append(f"default={self.default!r}")
        return f"{cn}({', '.join(args)})"

    @classmethod
    @no_type_check
    def from_full_annotation(
        cls, name: str, full_annotation: Annotated | Any, *, default: Any = NoDefault
    ) -> "Field":
        """Creates a field from a full annotation."""
        base_type, anno_args = split_annotation(full_annotation)
        return cls(name, base_type, anno_args, default=default)

    @property
    def name(self) -> str:
        """The name of the field.

        This is guaranteed to be a valid Python identifier.
        """
        return self.__name  # type: ignore

    @property
    def base_type(self) -> type:
        """The base type of the annotation.

        FIXME: Make sure this is always a type.
        """
        return self.__base_type  # type: ignore

    @property
    def anno_args(self) -> tuple[Any, ...]:
        """Arguments of the annotation. May be empty."""
        return self.__anno_args  # type: ignore

    @property
    def has_args(self) -> bool:
        """Whether this field had any arguments."""
        return len(self.anno_args) > 0

    @no_type_check
    def get_full_annotation(self) -> Annotated | type:
        """Re-creates the original annotation."""
        if self.has_args:
            return create_annotation(self.base_type, *self.anno_args)
        return self.base_type

    @property
    def full_annotation(self):
        """The original, full annotation."""
        return self.get_full_annotation()

    @property
    def default(self) -> Any:
        """The default value."""
        return self.__default


@no_type_check
def _get_ns(module_name: str | None) -> dict | None:
    import sys

    try:
        mod = sys.modules[module_name]
    except KeyError:
        return None
    else:
        return mod.__dict__


def _is_fieldable(name: str, value: Any) -> bool:
    """Whether we should convert the value to a field."""
    if is_private(name):
        return False
    if isinstance(value, (FunctionType, property, classmethod, staticmethod, type)):
        return False
    # TODO: Check for other cases?
    return True


def _is_ignored(name: str, value: Any) -> bool:
    """Whether we should ignore this value entirely."""
    return False


class AnnoMeta(ABCMeta):
    """Metaclass for Annodized objects."""

    def __new__(mcs, name: str, bases, namespace: dict[str, Any], **kwargs):
        """Creates the proper Annode (sub)class."""

        # Collect annotations
        annotations: dict[str, Any] = {}
        if namespace.get("__module__") != AnnoMeta.__module__:
            globalns = _get_ns(namespace.get("__module__"))
            localns = None
            # FIXME: Is this doing the same thing twice? Too tired to tell.
            tmp = type(
                name, (), {"__annotations__": namespace.get("__annotations__", {})}  # type: ignore
            )
            # tmp = type(name, (), namespace)
            raw_annotations: dict[str, Any] = get_type_hints(
                tmp,
                globalns,
                localns,
                include_extras=True,
            )
            for ann_name, ann_type in raw_annotations.items():
                proper_type = eval_type(ann_type, globalns, localns)
                annotations[ann_name] = proper_type

        # Collect default values (& preserve unused fields)
        preserved: dict[str, Any] = {}
        default_values: dict[str, Any] = {}
        for var_name, var_value in namespace.items():
            if _is_fieldable(var_name, var_value):
                default_values[var_name] = var_value
            elif _is_ignored(var_name, var_value):
                continue
            else:
                preserved[var_name] = var_value

        # Create fields
        fields: dict[str, Field] = {}
        # Inherit fields
        for base in reversed(bases):
            base_fields = getattr(base, "__fields__", {})
            for bfname, bfield in base_fields.items():
                assert isinstance(bfield, Field)
                fields[bfname] = bfield
        # Add fields from our annotations and defaults
        field_keys = list(annotations.keys())
        field_keys += [x for x in default_values.keys() if x not in field_keys]
        for key in field_keys:
            fld = Field.from_full_annotation(
                key,
                annotations.get(key, Any),
                default=default_values.get(key, NoDefault),
            )
            fields[key] = fld

        # Create the namespace
        new_namespace = dict(__fields__=fields, **preserved)
        # Finally, create the class
        cls = super().__new__(mcs, name, bases, new_namespace, **kwargs)
        return cls


class Annode(metaclass=AnnoMeta):
    """Base class for annotated things."""

    if TYPE_CHECKING:
        __fields__: ClassVar[dict[str, Field]] = {}

    def __init__(__init_self__, **data: Any) -> None:
        """Creates the object based on the fields."""
        res_data = check_init(type(__init_self__), **data)
        for k, v in res_data.items():
            object.__setattr__(__init_self__, k, v)

    def __setattr__(self, name: str, value: Any) -> None:
        """Sets the value, possibly applying checks."""
        res = check_setattr(self, name, value)
        return object.__setattr__(self, name, res)

    def __repr__(self) -> str:
        """String representation of this class."""
        cn = type(self).__qualname__
        args = []
        for key, fld in type(self).__fields__.items():
            v = getattr(self, key, fld.default)
            if v != fld.default:
                args.append(f"{key}={v!r}")
        return f"{cn}({', '.join(args)})"


def check_init(cls: type[Annode], **data: Any) -> dict[str, Any]:
    """Runs the initialization conversions."""
    # Calculate field requirements
    has_default = {k for k, v in cls.__fields__.items() if v.default is not NoDefault}
    not_required = has_default  # FIXME: support Required[] and NotRequired[]
    required = set(cls.__fields__.keys()).difference(not_required)

    # Fill values
    filled_values = {k: cls.__fields__[k].default for k in not_required}
    filled_values.update(data)  # FIXME: Maybe only valid keys?...

    # Manipulate values (conversion, type checking, etc. via plugins)
    # TODO

    # Check whether all required were filled
    missing = required.difference(filled_values.keys())
    if len(missing) > 0:
        raise ValueError(f"Missing required fields: {missing}")
    # Return all the filled values
    return filled_values


def check_setattr(obj: Annode, name: str, value: Any) -> Any:
    """Runs the setattr conversions."""
    # Check whether we just set it without thinking :)
    if is_private(name):
        return value

    # Manipulate value (via plugins)
    # TODO

    # Check validity
    if name not in type(obj).__fields__.keys():
        # FIXME: Reject?
        pass

    return value
