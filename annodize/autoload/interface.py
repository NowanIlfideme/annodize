"""Auto-loading interface."""

from typing import Any, Callable, Protocol, TypeVar

import fsspec
from fsspec.core import OpenFile


class Loadable(Protocol):
    """Loadable object."""


class Saveable(Protocol):
    """Saveable object."""


class Roundtrippable(Loadable, Saveable):
    """Both loadable and saveable object.

    Essentially, this is Intersection[Loadable, Saveable].
    """


Loader = Callable[[OpenFile], Loadable]
Saver = Callable[[OpenFile, Saveable], None]

_TRL = TypeVar("_TRL", bound=type[Roundtrippable] | type[Loadable])
_TRS = TypeVar("_TRS", bound=type[Roundtrippable] | type[Saveable])
_TR = TypeVar("_TR", bound=type[Roundtrippable])


class Registry(object):
    """Registry that enables loading and saving objects."""

    __slots__ = ("__loaders", "__savers")

    def __init__(self):
        self.__loaders: dict[_TRL, Loader] = {}
        self.__savers: dict[_TRS, Saver] = {}

    @property
    def types_loadable(self) -> set[_TRL]:
        """Types that are loadable."""
        return set(self.__loaders.keys())

    @property
    def types_saveable(self) -> set[_TRS]:
        """Types that are saveable."""
        return set(self.__savers.keys())

    @property
    def types_rt(self) -> set[_TR]:
        """Types that are round-trippable (loadable and saveable)."""
        tl = self.types_loadable
        ts = self.types_saveable
        return ts.intersection(tl)  # type: ignore

    def __repr__(self) -> str:
        cn = type(self).__qualname__
        n_load = len(self.types_loadable)
        n_save = len(self.types_saveable)
        n_rt = len(self.types_rt)
        return f"<{cn} with {n_rt} rt, {n_load} loadable, {n_save} saveable>"

    def infer_loader(self, kls: _TRL) -> Loader:
        """Infers the loader given the class."""
        raise NotImplementedError("Inferring not implemented!")

    def infer_saver(self, kls: _TRS) -> Saver:
        """Infers the saver given the class."""
        raise NotImplementedError("Inferring not implemented!")

    def register_loadable(self, kls: _TRL, loader: Loader | None = None) -> _TRL:
        """Registers this class as loadable."""
        if loader is None:
            loader = self.infer_loader(kls)
        # TODO: Implement checks!
        self.__loaders[kls] = loader
        return kls

    def register_saveable(self, kls: _TRS, saver: Saver | None = None) -> _TRS:
        """Registers this class as saveable."""
        if saver is None:
            saver = self.infer_saver(kls)
        # TODO: Implement!
        self.__savers[kls] = saver
        return kls

    def register_rt(
        self, kls: _TR, loader: Loader | None = None, saver: Saver | None = None
    ) -> _TR:
        """Registers this class as roundtrippable (both saveable and loadable)."""
        kls = self.register_loadable(kls, loader=loader)
        kls = self.register_saveable(kls, saver=saver)
        return kls

    # Save/load registered classes

    def save_registered(self, obj: Saveable, of: OpenFile | Any) -> None:
        """Saves a known Saveable object to a path."""
        kls = type(obj)
        if kls not in self.__savers:
            raise TypeError(f"Unknown saveable class: {kls!r}")
        if not isinstance(of, OpenFile):
            of = fsspec.open(of, mode="wb")
        saver = self.__savers[kls]
        return saver(of, obj)

    def load_registered(self, kls: type[Loadable], of: OpenFile | Any) -> Loadable:
        """Loads a known Loadable type from a file."""
        if kls not in self.__loaders:
            raise TypeError(f"Unknown loadable class: {kls!r}")
        if not isinstance(of, OpenFile):
            of = fsspec.open(of, mode="rb")
        loader = self.__loaders[kls]
        return loader(of)

    # Loading with inferring the type

    def load_infer_registered(self, of: OpenFile | Any) -> Loadable:
        """Loads a known Loadable type from a self-describing file.

        This infers the type based on the file.
        FIXME: Not implemented.
        """
        if not isinstance(of, OpenFile):
            of = fsspec.open(of, mode="rb")
        with of as f:
            raise NotImplementedError("Not implemented!")
