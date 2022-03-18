"""General schema definitions."""

from typing import Iterable, TypeVar

from annodize.field import Field, NamespaceFields

DataType = TypeVar("DataType")
DFType = TypeVar("DFType")


class Column(object):
    """A dataframe column definition.

    Attributes
    ----------
    name : str
        The column name.
    datatype : DataType
        The data type of the column. TODO: allowed types?...
    nullable : bool
        Whether the column can contain null values. Default is False.
    required : bool
        Whether the column must be in the schema. Default is True.
    """

    __slots__ = ("__name", "__datatype", "__required", "__nullable")

    def __init__(
        self,
        name: str,
        datatype: DataType,
        *,
        nullable: bool = False,
        required: bool = True,
    ):
        self.__name = str(name)
        self.__datatype = datatype  # TODO: Check
        self.__nullable = bool(nullable)
        self.__required = bool(required)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def datatype(self) -> DataType:
        return self.__datatype

    @property
    def nullable(self) -> bool:
        return self.__nullable

    @property
    def required(self) -> bool:
        return self.__required

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        parts = [repr(self.name), repr(self.datatype)]
        if self.nullable:
            parts.append("nullable=True")
        if not self.required:
            parts.append("required=False")
        return f"{cn}({', '.join(parts)})"

    @classmethod
    def from_field(cls, field: Field) -> "Column":
        """Creates a Column from a passed Field."""
        datatype = field.type_  # FIXME: proper type checking
        col = cls(field.name, datatype, nullable=False, required=True)  # type: ignore
        return col


class Schema(object):
    """A dataframe schema definition, inspired by Spark schema.

    This is meant to be library-agnostic by way of plugins.

    TODO
    ----
    - Plugin system for dataframe types.
    - Custom validation error hierarchy, a-la pydantic or pandas-schema.
    """

    __slots__ = ("__columns",)

    def __init__(self, columns: Iterable[Column]):
        self.__columns = tuple(columns)

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        cols2 = list(self.columns)
        return f"{cn}({cols2!r})"

    @property
    def columns(self) -> tuple[Column, ...]:
        return self.__columns

    @classmethod
    def from_namespace_fields(cls, nsp_fields: NamespaceFields) -> "Schema":
        """Creates a Schema from passed namespace fields."""
        cols = [Column.from_field(fld) for fld in nsp_fields.fields]
        return cls(cols)

    def validate(self, df: DFType, *, raise_on_error: bool = True) -> Exception | None:
        """Validates the dataframe according to this schema, returning any errors."""
        err = None
        if (err is not None) and raise_on_error:
            raise err
        return err

    def enforce(self, df: DFType) -> DFType:
        """Attempts to convert the passed dataframe to adhere to this schema."""
        return df
