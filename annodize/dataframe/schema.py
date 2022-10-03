"""Defining a (possibly recursive) schema."""

from typing import Any, Callable, TypeVar

DF = TypeVar("DF")
"""Generic dataframe type."""


class Field:
    """Dataframe field definition."""

    __slots__ = "__name", "__type", "__default", "__checks", "__extra_annotations"

    NO_DEFAULT = ...

    def __init__(
        self,
        name: str,
        type_: type,
        default: Any = NO_DEFAULT,
        annotations: list[Any] = [],
    ):
        self.__name = name
        self.__type = type_
        self.__default = default
        self.__checks: list = []  # TODO:
        self.__extra_annotations = list(annotations)

    @classmethod
    def from_annotation(cls, ann: str | Any) -> "Field":
        """Gets the field from the annotation."""
        # TODO: Make sure to support string-type annotations... hacky I guess.
        raise NotImplementedError("TODO.")

    @property
    def name(self) -> str:
        """The name of the field."""
        return self.__name

    @property
    def type_(self) -> type:
        """The type of the field."""
        return self.__type

    @property
    def default(self) -> Any:
        """The default value of the field."""
        return self.__default

    @property
    def checks(self) -> list:
        """Checks identified from annotations."""
        return list(self.__checks)

    @property
    def extra_annotations(self) -> list[Any]:
        """Any annotations not identified as checks."""
        return list(self.__extra_annotations)


class GlobalCheck:
    """Global dataframe check."""


class SchemaSpecificGlobalCheck(GlobalCheck):
    """Schema-specific global check."""

    def __init__(self, func: "SchemaCheck"):
        self.__func = func


def global_check(func: "SchemaCheck") -> SchemaSpecificGlobalCheck:
    """Registers this function as a schema-specific global check."""
    return SchemaSpecificGlobalCheck(func)


class Schema:
    """Dataframe schema definition.

    TODO: Probably needs a metaclass or something.
    """

    @classmethod
    def validate(cls, df: DF) -> "DFValidationError" | None:
        """Validates the dataframe, returning errors."""
        from .api import plugin_manager

        chk = plugin_manager.get_checker_for(df)
        return chk(cls, df)

    @classmethod
    def enforce(cls, df: DF, always: bool = False) -> None:
        """Asserts that the dataframe complies with the schema.

        NOTE: This is ignored if running with debugging optimized, i.e. `python -O`
        """
        if not (__debug__ or always):
            # Running in optimized mode - ignore
            return

        err = cls.validate(df)
        if err is not None:
            raise err

    @classmethod
    def coerce(cls, df: DF) -> DF:
        """Coerces the dataframe to conform to the schema, if possible."""
        raise NotImplementedError("Not yet implemented at all.")

    @classmethod
    def fields(cls) -> list[Field]:
        """Returns all the fields of this class."""
        raise NotImplementedError("TODO.")

    @classmethod
    def global_checks(cls) -> list[GlobalCheck]:
        """Returns all global checks of this class."""
        raise NotImplementedError("TODO.")


class DFValidationError(ValueError):
    """Dataframe validation failed (one or more errors)."""

    # TODO: Location, wrap multiple errors, etc.


InstanceCheck = Callable[[DF], bool]
SchemaCheck = Callable[[type[Schema], DF], DFValidationError | None]
