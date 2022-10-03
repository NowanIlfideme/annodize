"""Unit tests for schema definition."""


import pytest

from annodize.dataframe.schema import DF
from annodize.dataframe.test.conftest import ExSchema1, df_col, df_row


@pytest.mark.parametrize("df", [df_col, df_row])
def test_generic(df: DF):
    """Tests generic functionality."""
    ExSchema1
