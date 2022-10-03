"""Implementation of a row-major dataframe type, with schema checks."""

from typing import Any, TypeGuard

from annodize.dataframe.plugin_loader import PluginManager
from annodize.dataframe.schema import DF, DFValidationError, Schema

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


def check_schema(schema: type[Schema], df: RowMajorDF) -> DFValidationError | None:
    """Schema checker for row-major 'dataframes'."""
    # TODO: Implement


def register_plugin(mgr: PluginManager, plugin_name: str):
    """Row-major plugin entry point."""
    mgr.register_instance_check(is_row_major, plugin_name=plugin_name)
    mgr.register_schema_check(check_schema, plugin_name=plugin_name)
