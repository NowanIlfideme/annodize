"""Example `annodize.dataframe` plugin implementation.

Note that this is specified in the `entry_points` of your package.
"""

from annodize.dataframe.example.col_major import is_col_major
from annodize.dataframe.example.row_major import is_row_major
from annodize.dataframe.plugin_loader import PluginManager


def register_col_major(mgr: PluginManager, plugin_name: str):
    """Column-major plugin entry point."""
    mgr.register_instance_check(is_col_major, plugin_name=plugin_name)


def register_row_major(mgr: PluginManager, plugin_name: str):
    """Row-major plugin entry point."""
    mgr.register_instance_check(is_row_major, plugin_name=plugin_name)
