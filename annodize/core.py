"""Core objects for ."""

from typing import Annotated, Any, Callable, Iterable, ParamSpec, TypeVar

P = ParamSpec("P")  # args and kwargs
RT = TypeVar("RT")  # return type


class BaseHook(object):
    """Base hook for working with annotations."""

    def __init_subclass__(cls) -> None:
        """Checks user-made subclasses for correctness."""
        # TODO: check __call__ signature

    def __init__(self, *, enabled: bool = True):
        self.enabled = enabled

    def __repr__(self) -> str:
        """Simple string representation of this class.

        FIXME: Smart auto-repr from __init__
        """
        cn = type(self).__qualname__
        ss = f"enabled={self.enabled!r}" if not self.enabled else ""
        return f"{cn}({ss})"

    @property
    def enabled(self) -> bool:
        """Whether this hook is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, v):
        self._enabled = bool(v)

    def __call__(self, func: Callable[P, RT]) -> Callable[P, RT]:
        """Applies this hook to the called function.

        NOTE: This shouldn't change the function's signature.
        This requirement might be removed in the future...
        """
        return func

    @classmethod
    def deep_inspect(cls, func: Callable[P, RT]):
        """Utility method that provides deep inspection of the function."""

        # TODO: Implement.

    def __rshift__(self, other: Any) -> "CompositeHook":
        """Chains this hook with another one following it."""
        children = (*_flatten_hook(self), *_flatten_hook(other))
        return CompositeHook(children)


class CompositeHook(BaseHook):
    """A hook that consists of several sub-hooks, to be invoked in succession."""

    def __init__(self, children: Iterable[BaseHook], *, enabled: bool = True):
        self._children = tuple(children)
        super().__init__(enabled=enabled)

    def __repr__(self) -> str:
        """Simple string representation of this class."""
        cn = type(self).__qualname__
        args = [f"{self.children!r}"]
        if not self.enabled:
            args.append(f"enabled={self.enabled!r}")
        return f"{cn}({', '.join(args)})"

    @property
    def children(self) -> tuple[BaseHook, ...]:
        """The sub-hooks used by this hook."""
        return self._children

    def __call__(self, func: Callable[P, RT]) -> Callable[P, RT]:
        """Applies all children hooks, one after the other."""
        res = func
        for child in self.children:
            res = child(res)
        return res


def as_hook(obj: Any) -> BaseHook:
    """Converts the passed object to a hook, if possible."""
    if isinstance(obj, BaseHook):
        return obj
    raise NotImplementedError(f"`as_hook()` not implemented for {obj!r}")


def _flatten_hook(obj: Any) -> tuple[BaseHook, ...]:
    """Converts the passed object into a tuple of 1+ hooks."""
    if isinstance(obj, CompositeHook):
        return tuple(obj.children)
    if isinstance(obj, BaseHook):
        return (obj,)
    return _flatten_hook(as_hook(obj))
