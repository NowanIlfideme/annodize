"""Pytest configuration and such."""

from typing import Annotated, Optional

from annodize.dataframe.example import ColMajorDF, RowMajorDF, col_to_row
from annodize.dataframe.field_types import Nullable
from annodize.dataframe.schema import DF, DFValidationError, Schema, global_check


class ExSchema1(Schema):
    """Example schema 1."""

    a1: Annotated[str, Nullable]
    a2: Nullable[str]  # type: ignore
    b: str
    c: Optional[str]  # field is optional, but not nullable!

    @global_check
    def always_succeeds(cls, df: DF) -> DFValidationError | None:
        """Global check that always succeeds."""


class ExSchema2(Schema):
    """Example schema 2."""

    a1: str
    a2: str
    # check if extras

    @global_check
    def always_fails(cls, df: DF) -> DFValidationError | None:
        """Global check that always fails."""
        return DFValidationError()


df_col: ColMajorDF = {
    "a1": ["hi", None],
    "a2": ["hi2", None],
    "b": ["x", "x"],
}

df_row: RowMajorDF = col_to_row(df_col)
