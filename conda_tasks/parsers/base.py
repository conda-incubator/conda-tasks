"""Abstract base class for task file parsers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from ..models import Task


class TaskFileParser(ABC):
    """Interface that every task file parser must implement."""

    extensions: ClassVar[tuple[str, ...]] = ()
    filenames: ClassVar[tuple[str, ...]] = ()

    @abstractmethod
    def can_handle(self, path: Path) -> bool:
        """Return True if this parser knows how to read *path*."""

    @abstractmethod
    def parse(self, path: Path) -> dict[str, Task]:
        """Parse *path* and return a mapping of task-name -> Task."""

    @abstractmethod
    def add_task(self, path: Path, name: str, task: Task) -> None:
        """Persist a new task definition into *path*."""

    @abstractmethod
    def remove_task(self, path: Path, name: str) -> None:
        """Remove the task named *name* from *path*."""
