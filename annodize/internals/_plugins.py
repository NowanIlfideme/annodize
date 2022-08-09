"""Plugin loading, using the standard entry_points mechanism.

See Also
--------
https://docs.python.org/3/library/importlib.metadata.html#entry-points
https://setuptools.pypa.io/en/latest/userguide/entry_point.html#advertising-behavior
"""

from importlib.metadata import EntryPoint, entry_points


def load_plugins():
    """Loads the plugins."""
    eps = entry_points(group="annodize.plugins")
    # TODO: Catch exceptions, then raise them all
    for ep in eps:
        assert isinstance(ep, EntryPoint)
        plugin_loader = ep.load()
        plugin_loader()
