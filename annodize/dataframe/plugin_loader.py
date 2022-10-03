"""Loads `annodize.dataframe` plugins."""

import importlib.metadata as _im
import logging
from typing import Callable

from annodize.dataframe.schema import DF, InstanceCheck, SchemaCheck

logger = logging.getLogger(__name__)


class PluginManager:
    """Plugin manager class."""

    __slots__ = ("__instance_checks", "__schema_checks")

    def __init__(self):
        """Creates a blank slate, with no plugins."""
        self.__instance_checks: list[tuple[InstanceCheck, str]] = []
        self.__schema_checks: dict[str, SchemaCheck] = {}

    def load_plugins(self):
        """Loads all plugins."""
        eps: _im.EntryPoints = _im.entry_points(group="annodize.dataframe")
        # FIXME: Check why entry points are sometimes doubled...
        for ep_i in eps:
            plugin_name = ep_i.name
            try:
                func: Callable[[PluginManager, str], None] = ep_i.load()
                func(self, plugin_name)
            except Exception:
                logger.exception(f"Failed to load plugin for: {plugin_name!r}")

    def register_instance_check(self, func: InstanceCheck, plugin_name: str):
        """Registers `func` as an instance check for your plugin's dataframe type."""
        # TODO: inspect whether func is a valid InstanceCheck
        self.__instance_checks.append((func, plugin_name))

    def get_plugin_for(self, df: DF) -> str:
        """Gets the plugin for the passed dataframe."""
        for func, plugin_name in self.__instance_checks:
            try:
                if func(df):
                    return plugin_name
            except Exception:
                continue
        raise TypeError(f"No plugins available for dataframe of type {type(df)!r}")

    def register_schema_check(self, func: SchemaCheck, plugin_name: str):
        """Registers `func` as the schema checker for your plugin."""
        # TODO: inspect whether func is a valid SchemaCheck
        if plugin_name in self.__schema_checks.keys():
            logger.warning(f"Schema checker already exists for plugin {plugin_name!r}")
        self.__schema_checks[plugin_name] = func

    def get_checker_for(self, df: DF) -> SchemaCheck:
        """Gets the schema check function for a dataframe type."""
        plg = self.get_plugin_for(df)
        chk = self.__schema_checks.get(plg)
        if chk is None:
            raise TypeError(f"No schema check defined for plugin {plg!r}")
        return chk


if __name__ == "__main__":
    manager = PluginManager()
    manager.load_plugins()
