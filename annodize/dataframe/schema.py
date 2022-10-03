"""Defining a (possibly recursive) schema."""

from typing import TypeVar

DF = TypeVar("DF")
"""Generic dataframe type."""


class DFValidationError(ValueError):
    """Dataframe validation failed."""


class Schema:
    """Dataframe schema definition."""

    @classmethod
    def validate(cls, df: DF) -> DFValidationError | None:
        """Validates the dataframe."""

    @classmethod
    def enforce(cls, df: DF) -> None:
        """Enforces the dataframe to"""

    @classmethod
    def coerce(cls, df: DF) -> DF:
        """Coerces the dataframe into the schema, if possible."""
