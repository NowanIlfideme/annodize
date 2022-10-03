"""Tests plugins."""


from annodize.dataframe.plugin_loader import PluginManager
from annodize.dataframe.test.conftest import df_col, df_row


def test_plugin_load():
    """Tests loading plugins."""
    manager = PluginManager()
    manager.load_plugins()
    assert manager.get_plugin_for(df_col) == "example_col_major"
    assert manager.get_plugin_for(df_row) == "example_row_major"
