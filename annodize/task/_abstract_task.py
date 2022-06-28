"""Task definition."""


from typing import Any, Callable, List


class NamedObject(object):
    """Named objects."""

    def __init__(self, name: str):
        self.__name = str(name)

    @property
    def name(self) -> str:
        return self.__name

    def __repr_parts__(self) -> List[str]:
        return [repr(self.name)]

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        pt = ", ".join(self.__repr_parts__())
        return f"{cn}({pt})"


class AbstractInput(NamedObject):
    """Defines an input placeholder."""


class AbstractOutput(NamedObject):
    """Defines an output placeholder."""


class AbstractArtifact(NamedObject):
    """The abstract definition of an artifact."""


class AbstractTask(NamedObject):
    """The abstract definition of a task."""

    def __init__(
        self,
        name: str,
        *,
        inputs: List[AbstractInput] = [],
        outputs: List[AbstractOutput] = [],
    ):
        super().__init__(name)
        self.__inputs = list(inputs)
        self.__outputs = list(outputs)

    def __repr_parts__(self) -> List[str]:
        parts = [repr(self.name)]
        if len(self.inputs) > 0:
            parts.append(f"inputs={self.inputs!r}")
        if len(self.outputs) > 0:
            parts.append(f"outputs={self.outputs!r}")
        return parts

    @property
    def inputs(self) -> List[AbstractInput]:
        return list(self.__inputs)

    @property
    def outputs(self) -> List[AbstractOutput]:
        return list(self.__outputs)


class PyFunctionTask(AbstractTask):
    """Python function task."""

    def __init__(
        self,
        name: str,
        wrapped: Callable,
        *,
        inputs: List[AbstractInput] = [],
        outputs: List[AbstractOutput] = [],
    ):
        super().__init__(name, inputs=inputs, outputs=outputs)
        self.__wrapped = wrapped

    def __repr_parts__(self) -> List[str]:
        parts = super().__repr_parts__()
        parts.insert(1, repr(self.wrapped))
        return parts

    @property
    def wrapped(self) -> Callable:
        return self.__wrapped
