"""Base adapter interface for all integrations."""

from abc import ABC, abstractmethod
from typing import Any


class SourceAdapter(ABC):
    """Fetches data from an external service."""

    @abstractmethod
    def fetch(self, config: dict[str, Any]) -> dict[str, Any]:
        ...


class SinkAdapter(ABC):
    """Pushes results to an external service."""

    @abstractmethod
    def push(self, data: dict[str, Any], config: dict[str, Any]) -> None:
        ...
