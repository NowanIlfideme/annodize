"""Extended `typing` module, using `typing_extensions` and `typingx`."""

import sys
from typing import (
    IO,
    TYPE_CHECKING,
    AbstractSet,
    Any,
    AsyncContextManager,
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    BinaryIO,
    ByteString,
    Callable,
    ChainMap,
    ClassVar,
    Collection,
    Container,
    ContextManager,
    Coroutine,
    Counter,
    DefaultDict,
    Deque,
    Dict,
    Final,
    ForwardRef,
    FrozenSet,
    Generator,
    Generic,
    Hashable,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    List,
    Mapping,
    MappingView,
    Match,
    MutableMapping,
    MutableSequence,
    MutableSet,
    NamedTuple,
    NewType,
    NoReturn,
    Optional,
    OrderedDict,
    Pattern,
    Protocol,
    Reversible,
    Sequence,
    Set,
    Sized,
    SupportsAbs,
    SupportsBytes,
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    SupportsRound,
    Text,
    TextIO,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    ValuesView,
    cast,
    final,
    no_type_check,
    overload,
    runtime_checkable,
)

from typing_extensions import Concatenate, ParamSpec, TypeGuard
from typingx import (
    Annotated,
    Listx,
    Literal,
    NoneType,
    Tuplex,
    TypedDict,
    TypeLike,
    func_check,
    get_args,
    get_origin,
    get_type_hints,
)
from typingx.typing_compat import display_type

# Snippet from https://github.com/samuelcolvin/pydantic/blob/master/pydantic/typing.py

if sys.version_info < (3, 9):

    def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:
        return type_._evaluate(globalns, localns)

else:

    def evaluate_forwardref(type_: ForwardRef, globalns: Any, localns: Any) -> Any:
        # Even though it is the right signature for python 3.9, mypy complains with
        # `error: Too many arguments for "_evaluate" of "ForwardRef"` hence the cast...
        return cast(Any, type_)._evaluate(globalns, localns, set())


@no_type_check
def eval_type(x, globalns, localns, recursive_guard=frozenset()):
    """Evaluate all forward references in the given type t.

    For use of globalns and localns see the docstring for get_type_hints().
    recursive_guard is used to prevent prevent infinite recursion
    with recursive ForwardRef.
    """
    from typing import _eval_type

    if isinstance(x, ForwardRef):
        x = evaluate_forwardref(x, globalns, localns)

    return _eval_type(x, globalns, localns, recursive_guard=recursive_guard)


def resolve_annotations(
    raw_annotations: Dict[str, Type[Any]], module_name: Optional[str]
) -> Dict[str, Type[Any]]:
    """Taken from Pydantic, which took partially from typing.get_type_hints.

    Resolve string or ForwardRef annotations into type objects if possible.
    """
    base_globals: Optional[Dict[str, Any]] = None
    if module_name:
        try:
            module = sys.modules[module_name]
        except KeyError:
            # happens occasionally, see https://github.com/samuelcolvin/pydantic/issues/2363
            pass
        else:
            base_globals = module.__dict__

    annotations = {}
    for name, value in raw_annotations.items():
        if isinstance(value, str):
            if (3, 10) > sys.version_info >= (3, 9, 8) or sys.version_info >= (
                3,
                10,
                1,
            ):
                value = ForwardRef(value, is_argument=False, is_class=True)
            else:
                value = ForwardRef(value, is_argument=False)
        try:
            value = eval_type(value, base_globals, None)
        except NameError:
            # this is ok, it can be fixed with update_forward_refs
            pass
        annotations[name] = value
    return annotations
