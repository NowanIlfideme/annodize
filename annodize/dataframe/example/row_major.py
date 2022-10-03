"""Implementation of a row-major dataframe type, with schema checks."""

from typing import Any, TypeGuard

from annodize.dataframe.ann import DF

RowMajorDF = list[dict[str, Any]]


def is_row_major(df: DF) -> TypeGuard[RowMajorDF]:
    """Checks if is a row-major 'dataframe'."""
    try:
        if isinstance(df, list):
            if len(df) == 0:
                return True  # We support 0-length dataframes
            row0 = df[0]
            if isinstance(row0, dict):
                return all(isinstance(k, str) for k in row0.keys())
    except Exception:
        pass
    return False
