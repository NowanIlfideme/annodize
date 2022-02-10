"""Foo."""

from makefun import wraps

from annodize.core import (
    P_HOOKED,
    P_ORIGINAL,
    RT_HOOKED,
    RT_ORIGINAL,
    Annotated,
    BaseHook,
    Callable,
    PrePostHook,
)


class HookA(PrePostHook):
    """Hook A."""

    def pre_call(
        self, *args: P_ORIGINAL.args, **kwargs: P_ORIGINAL.kwargs
    ) -> tuple[tuple, dict]:
        print(f"A found: args {args!r} and kwargs {kwargs!r} ")
        return args, kwargs


class HookB(PrePostHook):
    """Hook B."""

    def post_call(
        self,
        __return_value: RT_ORIGINAL,
        /,
        *args: P_ORIGINAL.args,
        **kwargs: P_ORIGINAL.kwargs,
    ) -> RT_HOOKED:
        print(f"B found: return value {__return_value!r}")
        return __return_value


hooks = HookA() >> HookB()


@hooks
def func(x: Annotated[str, object]) -> str:
    """Bah."""
    res = f"{x}_"
    print(f"Result: {res!r}")
    return res


if __name__ == "__main__":
    func("xxxx")
    help(func)
