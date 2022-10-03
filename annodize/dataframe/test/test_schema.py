"""Unit tests for schema definition."""


import pytest

from annodize.dataframe.schema import DF, DFValidationError
from annodize.dataframe.test.conftest import ExSchema1, ExSchema2, df_col, df_row


@pytest.mark.parametrize("df", [df_col, df_row])
def test_generic(df: DF):
    """Tests generic functionality."""
    ExSchema1.enforce(df)

    with pytest.raises(DFValidationError):
        ExSchema2.enforce(df)
