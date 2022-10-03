"""Example `annodize.dataframe` plugin implementation.

Note that this is specified in the `entry_points` of your package.
"""


def col_major():
    """Column-major plugin entry point."""
    print("col major loaded")


def row_major():
    """Row-major plugin entry point."""
    print("row major loaded")
