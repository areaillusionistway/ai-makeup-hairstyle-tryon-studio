"""Minimal service locator used across the studio.

Deliberately boring: no auto-wiring magic, no decorators. Handlers ask
for what they need by type, the container returns the singleton or
factory-produced instance. Keeps the boot path readable.
"""
from __future__ import annotations

from typing import Any, Callable, TypeVar, Type

from studio.config.settings import StudioSettings

T = TypeVar("T")


class Container:
    def __init__(self, settings: StudioSettings) -> None:
        self.settings = settings
        self._singletons: dict[type, Any] = {}
        self._factories: dict[type, Callable[["Container"], Any]] = {}

    def register_singleton(self, key: Type[T], instance: T) -> None:
        self._singletons[key] = instance

    def register_factory(self, key: Type[T], factory: Callable[["Container"], T]) -> None:
        self._factories[key] = factory

    def resolve(self, key: Type[T]) -> T:
        if key in self._singletons:
            return self._singletons[key]
        if key in self._factories:
            instance = self._factories[key](self)
            self._singletons[key] = instance
            return instance
        raise KeyError(f"nothing registered for {key!r}")