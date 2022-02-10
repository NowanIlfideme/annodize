"""Core objects for ."""

from typing import Annotated, Any, Callable, Generic, Iterable, ParamSpec, TypeVar, cast

from makefun import wraps

# Parameter spec
P_ORIGINAL = ParamSpec("P_ORIGINAL")
P_HOOKED = ParamSpec("P_HOOKED")

# Return type
RT_ORIGINAL = TypeVar("RT_ORIGINAL")
RT_HOOKED = TypeVar("RT_HOOKED")


class BaseHook(Generic[P_ORIGINAL, RT_ORIGINAL, P_HOOKED, RT_HOOKED]):
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

    def __call__(
        self, func: Callable[P_ORIGINAL, RT_ORIGINAL]
    ) -> Callable[P_HOOKED, RT_HOOKED]:
        """Applies this hook to the called function. This may change the signature."""
        return cast(Callable[P_HOOKED, RT_HOOKED], func)

    @classmethod
    def deep_inspect(cls, func: Callable[P_ORIGINAL, RT_ORIGINAL]):
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

    def __call__(
        self, func: Callable[P_ORIGINAL, RT_ORIGINAL]
    ) -> Callable[P_HOOKED, RT_HOOKED]:
        """Applies all children hooks, one after the other."""
        res = func
        for child in self.children:
            res = child(res)
        return cast(Callable[P_HOOKED, RT_HOOKED], res)


class PrePostHook(BaseHook):
    """Simple hook"""

    def pre_call(
        self, *args: P_ORIGINAL.args, **kwargs: P_ORIGINAL.kwargs
    ) -> tuple[tuple, dict]:
        """Does something to the arguments."""
        return cast(tuple, args), cast(dict, kwargs)

    def post_call(
        self,
        __return_value: RT_ORIGINAL,
        /,
        *args: P_ORIGINAL.args,
        **kwargs: P_ORIGINAL.kwargs,
    ) -> RT_HOOKED:
        """Does something to the return value, based on the original arguments and return value."""
        return cast(RT_HOOKED, __return_value)

    def __call__(
        self, func: Callable[P_ORIGINAL, RT_ORIGINAL]
    ) -> Callable[P_HOOKED, RT_HOOKED]:
        """Adds pre- and post-."""

        @wraps(func)
        def inner(*args, **kwargs):
            new_args, new_kwargs = self.pre_call(*args, **kwargs)
            res = func(*new_args, **new_kwargs)
            new_res = self.post_call(res, *args, **kwargs)
            return new_res

        return inner


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
