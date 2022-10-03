"""Unit tests for schema definition."""

from typing import Annotated, Optional

from annodize.dataframe.example import ColMajorDF, RowMajorDF, col_to_row
from annodize.dataframe.schema import Nullable, Schema


class ExSchema1(Schema):
    """Example schema 1."""

    a1: Annotated[str, Nullable]
    a2: Nullable[str]  # type: ignore
    b: Optional[str]  # field is optional, but not nullable!


def df_col() -> ColMajorDF:
    """Creates a column-major dataframe."""
    return {
        "a1": ["hi", None],
        "a2": ["hi2", None],
    }


def df_row() -> RowMajorDF:
    """Creates a row-major dataframe."""
    return col_to_row(df_col())


def test_generic():
    """Tests generic functionality."""
    ExSchema1
