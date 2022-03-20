"""Field collection for functions."""

from inspect import Signature
from typing import Annotated, Callable, Sequence

from ._field import Field
from ._repr import repr_sig


class FunctionFields(object):
    """A set of fields for a function/callable. All attributes are read-only.

    Attributes
    ----------
    input_fields : tuple[Field, ...]
        The `Field` objects corresponding to the arguments.
    output_field : Field
        The `Field` corresponding to the result, with `name` set to the function's name.
    signature : Signature
        The `inspect.Signature` of the function.

    TODO
    ----
    Possibly allow multiple outputs via `tuple[Annotated[type1, ann1], Annotated[type2, ann2]]`?
    Or do we need Fields within Fields?...
    """

    __slots__ = ("__input_fields", "__output_field", "__signature")

    def __init__(
        self, input_fields: Sequence[Field], output_field: Field, signature: Signature
    ):
        # Type checking
        i_flds = tuple(input_fields)
        assert all(isinstance(x, Field) for x in i_flds)
        assert isinstance(output_field, Field)
        # Ensure unique names
        assert len(set(x.name for x in i_flds) | {output_field.name}) == len(i_flds) + 1
        self.__input_fields = i_flds
        self.__output_field = output_field
        self.__signature = signature

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        xargs: list[str] = [
            repr(self.__input_fields),
            repr(self.__output_field),
            repr_sig(self.__signature),
        ]
        return cn + "(" + ", ".join(xargs) + ")"

    @property
    def signature(self) -> Signature:
        """The function's signature."""
        return self.__signature

    @property
    def input_fields(self) -> tuple[Field, ...]:
        """The fields for the input values (arguments)."""
        return tuple(self.__input_fields)

    @property
    def output_field(self) -> Field:
        """The field for the return value, named after the function."""
        return self.__output_field

    @classmethod
    def from_callable(cls, func: Callable) -> "FunctionFields":
        """Gets a set of fields from a callable."""
        assert callable(func)
        out_name = func.__name__
        # NOTE: out_name = "return" will currently raise an exception!
        # Maybe out_name = func.__qualname__ is better, though it isn't "allowed" right now.
        sig = Signature.from_callable(func)
        input_fields = tuple(
            Field.from_inspect_parameter(param) for param in sig.parameters.values()
        )
        output_field = Field(out_name, sig.return_annotation)
        return cls(input_fields, output_field, sig)


if __name__ == "__main__":

    def func(df: str) -> Annotated[str, "schema-here"]:
        return df

    ff = FunctionFields.from_callable(func)
