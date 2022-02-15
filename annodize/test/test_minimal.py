"""Minimal tests for CI."""


def test_module_importable():
    """Minimal test that the module imports correctly."""
    from annodize import __version__

    assert __version__ != ""
