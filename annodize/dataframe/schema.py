"""Defining a (possibly recursive) schema."""

from typing import Callable, TypeVar

DF = TypeVar("DF")
"""Generic dataframe type."""


class DFValidationError(ValueError):
    """Dataframe validation failed (one or more errors)."""

    # TODO: Location, wrap multiple errors, etc.


class Schema:
    """Dataframe schema definition."""

    @classmethod
    def validate(cls, df: DF) -> DFValidationError | None:
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


InstanceCheck = Callable[[DF], bool]
SchemaCheck = Callable[[type[Schema], DF], DFValidationError | None]
