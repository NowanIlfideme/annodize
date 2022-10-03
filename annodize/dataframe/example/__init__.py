"""Implementation examples of checks on built-in 'dataframe' types."""

__all__ = ["ColMajorDF", "RowMajorDF", "col_to_row", "row_to_col"]

from .col_major import ColMajorDF
from .row_major import RowMajorDF


def col_to_row(cdf: ColMajorDF) -> RowMajorDF:
    """Converts column-major dataframe to row-major (inefficiently)."""
    keys = list(cdf.keys())
    if len(keys) == 0:
        return []
    n = len(cdf[keys[0]])
    rows: RowMajorDF = []
    for i in range(n):
        rows.append({k: cdf[k][i] for k in keys})
    return rows


def row_to_col(rdf: RowMajorDF) -> ColMajorDF:
    """Converts row-major dataframe to column-major (inefficiently)."""
    keys = list(rdf[0].keys())
    cols: ColMajorDF = {k: [] for k in keys}
    for row in rdf:
        for k in keys:
            cols[k].append(row[k])
    return cols
