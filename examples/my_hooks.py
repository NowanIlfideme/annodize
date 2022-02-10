"""Foo."""

from makefun import wraps

from annodize import RT, Annotated, BaseHook, Callable, P


class HookA(BaseHook):
    """Hook A."""

    def __call__(self, func: Callable[P, RT]) -> Callable[P, RT]:
        """Prints 'A' before calling the function."""

        @wraps(func)
        def inner(*args, **kwargs):
            print("A")
            res = func(*args, **kwargs)
            return res

        return inner


class HookB(BaseHook):
    """Hook B."""

    def __call__(self, func: Callable[P, RT]) -> Callable[P, RT]:
        """Prints 'B: result' with the function's result."""

        @wraps(func)
        def inner(*args, **kwargs):
            res = func(*args, **kwargs)
            print(f"B: {res!r}")
            return res

        return inner


hooks = HookA() >> HookB()


@hooks
def func(x: Annotated[str, object]) -> str:
    """Bah."""
    return f"{x}_"


if __name__ == "__main__":
    res = func("xxxx")
    print(f"Result: {res!r}")
