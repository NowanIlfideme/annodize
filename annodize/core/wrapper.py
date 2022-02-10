"""Main wrapper class."""

from makefun import wraps

from annodize.ext.inspect import BoundArguments, Signature, signature
from annodize.ext.typing import (
    Any,
    Callable,
    ContextManager,
    Generic,
    ParamSpec,
    TypeVar,
    Union,
    cast,
    final,
)

P_IN = ParamSpec("P_IN")
P_OUT = ParamSpec("P_OUT")
RT_IN = TypeVar("RT_IN")
RT_OUT = TypeVar("RT_OUT")

# TODO: Create this Union dynamically

WrappableArg = Union["AnnodizeWrapper", ContextManager, Any]


@final  # type: ignore
class AnnodizeWrapper(Generic[P_IN, RT_IN, P_OUT, RT_OUT]):
    """Callable wrapper with automatic signature conversion."""

    def __init__(self, *steps: WrappableArg):
        """Creates the wrapper from wrappable arguments."""
        self.__steps = tuple(steps)

    @property
    def steps(self) -> tuple[WrappableArg, ...]:
        """The steps that this wrapper uses."""
        return tuple(self.__steps)

    def __convert_sig(self, sig_in: Signature) -> Signature:
        """Converts the signature from inner args to outer args."""
        sig_out = sig_in  # FIXME: Implement!
        return sig_out

    def __convert_args(self, bound_out: BoundArguments) -> BoundArguments:
        """Converts the bound arguments from outer arguments to inner arguments."""
        bound_in = bound_out  # FIXME: Implement!
        return bound_in

    def __convert_output(self, result_in: RT_IN) -> RT_OUT:
        """Converts the output result from inner function to outer function."""
        result_out = result_in  # FIXME: Implement!
        return cast(RT_OUT, result_out)

    def __call__(self, wrapped: Callable[P_IN, RT_IN], /) -> Callable[P_OUT, RT_OUT]:
        """Wraps the function with application of all the steps."""
        func_in = wrapped
        sig_in = signature(func_in)
        sig_out = self.__convert_sig(sig_in)

        @wraps(func_in, new_sig=sig_out)
        def outer_to_inner(*outer_args, **outer_kwargs):
            """Function that maps 'outer' to 'inner', calls the func, then maps back out."""
            # Convert out -> in
            bound_out = sig_out.bind(*outer_args, **outer_kwargs)
            bound_in = self.__convert_args(bound_out)
            # Res
            res_in = func_in(*bound_in.args, **bound_in.kwargs)
            # Convert in -> out
            res_out = self.__convert_output(res_in)
            return res_out

        func_out = cast(Callable[P_OUT, RT_OUT], outer_to_inner)  # for mypy
        return func_out
