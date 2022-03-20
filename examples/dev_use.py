"""Example of developer usage."""

from abc import ABCMeta
from inspect import BoundArguments
from typing import TYPE_CHECKING, Annotated, Any, Callable, ParamSpec, TypeVar

import pandas as pd
from makefun import wraps

from annodize import Field, FunctionFields, NamespaceFields

# The following is an example minimal implementation of schema validation


class SchemaMeta(ABCMeta):
    """Example metaclass for schemas."""

    def __new__(mcs, name: str, bases, namespace: dict[str, Any], **kwargs):
        """Creates the Schema type."""
        nsp_fields = NamespaceFields.from_namespace(namespace)
        new_namespace = {**namespace, "__fields__": nsp_fields}
        cls = super().__new__(mcs, name, bases, new_namespace, **kwargs)
        return cls


class Schema(metaclass=SchemaMeta):
    """Example schema definition class."""

    if TYPE_CHECKING:
        __fields__: NamespaceFields

    @classmethod
    def validate(cls, df: pd.DataFrame):
        """Ensures that `df` is bound by this schema."""
        errors: list[str] = []
        cols = list(df.columns)
        for fld in cls.__fields__.fields:
            if fld.name in cols:
                # TODO: type check or coerce?
                pass
            else:
                errors.append(f"Missing column: {fld.name!r}")
        if len(errors) > 0:
            raise ValueError(
                "The following errors were found during validation:\n"
                + "\n".join(errors)
            )
        return df


P = ParamSpec("P")
RT = TypeVar("RT")


def _filter_schemas(fld: Field) -> type[Schema] | None:
    """Gets a Schema, if one exists."""
    accepted_anns: list[type[Schema]] = []
    for arg in fld.ann_args:
        try:
            if issubclass(arg, Schema):
                accepted_anns.append(arg)
        except Exception:
            pass
    if len(accepted_anns) > 1:
        raise ValueError(f"Only one Schema allowed per output.")
    elif len(accepted_anns) == 1:
        return accepted_anns[0]
    return None


def check_schemas(func: Callable[P, RT]) -> Callable[P, RT]:
    """Decorator to check that schemas"""

    ff = FunctionFields.from_callable(func)

    # Input schemas
    input_schemas: dict[str, type[Schema]] = {}
    for in_fld in ff.input_fields:
        in_sch = _filter_schemas(in_fld)
        if in_sch is not None:
            input_schemas[in_fld.name] = in_sch

    # Output schema
    # FIXME: Allow multiple outputs, maybe?
    output_schema: type[Schema] | None = _filter_schemas(ff.output_field)

    # Signature
    sig = ff.signature

    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> RT:
        """Inner function that runs the validation."""
        # Check inputs
        updates = {}
        bound_orig = sig.bind(*args, **kwargs)
        bound_orig.apply_defaults()
        for k, sch in input_schemas.items():
            df_i = bound_orig.arguments[k]
            df_i_fixed = sch.validate(df_i)
            updates[k] = df_i_fixed

        # Apply updates
        arguments_upd = dict(bound_orig.arguments)
        arguments_upd.update(updates)
        bound_upd = BoundArguments(sig, arguments_upd)

        # Run user function
        res_orig = func(*bound_upd.args, **bound_upd.kwargs)

        # Check the output
        if output_schema is None:
            res_upd = res_orig
        else:
            res_upd = output_schema.validate(res_orig)
        return res_upd

    return inner


# ANOTHER LIBRARY

Input = lambda x: x
Output = lambda x: x


class JobGraph:
    def register(self, func):
        return func


job_graph = JobGraph()


# User interface


class SchemaA(Schema):
    """My input dataframe schema."""

    x: float
    y: float


class SchemaB(Schema):
    """My output dataframe schema."""

    x: Annotated[float, "checkme"]
    y: float
    z: float


@job_graph.register
@check_schemas
def func(
    df: Annotated[pd.DataFrame, SchemaA, Input("foo")],
    mult: Annotated[float, Input("bar")] = 1,
) -> Annotated[pd.DataFrame, SchemaB, Output("baz")]:
    """Function that transforms dataframes."""
    return df.assign(z=df["x"] + mult * df["y"])


df1 = pd.DataFrame({"x": [0.0, 1.0], "y": [1.0, -1.0]})
df2 = pd.DataFrame({"ex": [0.0, 1.0], "why": [1.0, -1.0]})

func(df1)
try:
    func(df2)
except ValueError as e:
    print("Correctly caught the error.")
    print(e)

func
