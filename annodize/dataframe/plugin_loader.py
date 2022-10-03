"""Loads `annodize.dataframe` plugins."""

import importlib.metadata as _im
import warnings
from typing import Callable

from annodize.dataframe.ann import DF

InstanceCheck = Callable[[DF], bool]


class PluginManager:
    """Plugin manager class."""

    def __init__(self):
        """Creates a blank slate, with no plugins."""
        self.__funcs: list[tuple[InstanceCheck, str]] = []

    def load_plugins(self):
        """Loads all plugins."""
        eps: _im.EntryPoints = _im.entry_points(group="annodize.dataframe")
        for ep_i in eps:
            plugin_name = ep_i.name
            try:
                func: Callable[[PluginManager, str], None] = ep_i.load()
                func(self, plugin_name)
            except Exception:
                warnings.warn(f"Failed to load plugin for: {plugin_name!r}")

    def register_instance_check(self, func: InstanceCheck, plugin_name: str):
        """Registers `func` as an instance check for your plugin's dataframe type."""
        self.__funcs.append((func, plugin_name))

    def get_plugin_for(self, df: DF) -> str:
        """Gets the plugin for the passed dataframe type."""
        for func, plugin_name in self.__funcs:
            try:
                if func(df):
                    return plugin_name
            except Exception:
                continue
        raise TypeError(f"No plugins available for dataframe of type {type(df)!r}")


if __name__ == "__main__":
    manager = PluginManager()
    manager.load_plugins()
