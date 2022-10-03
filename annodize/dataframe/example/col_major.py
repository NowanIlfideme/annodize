"""Implementation of a column-major dataframe type, with schema checks."""

from typing import Any, TypeGuard

from annodize.dataframe.ann import DF
from annodize.dataframe.plugin_loader import PluginManager

ColMajorDF = dict[str, list[Any]]


def is_col_major(df: DF) -> TypeGuard[ColMajorDF]:
    """Checks if is a column-major 'dataframe'."""
    try:
        if isinstance(df, dict):
            if len(df) == 0:
                return True  # We support no-column dataframes
            for k, v in df.items():
                if not (isinstance(k, str) and isinstance(v, list)):
                    return False
            return True
    except Exception:
        pass
    return False


def register_plugin(mgr: PluginManager, plugin_name: str):
    """Column-major plugin entry point."""
    mgr.register_instance_check(is_col_major, plugin_name=plugin_name)
