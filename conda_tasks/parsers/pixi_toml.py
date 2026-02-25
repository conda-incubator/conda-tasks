"""Parser for pixi.toml [tasks] and [target.<platform>.tasks] tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

import tomlkit

from ..exceptions import TaskParseError
from .base import TaskFileParser
from .normalize import normalize_override, normalize_task

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from ..models import Task


class PixiTomlParser(TaskFileParser):
    """Reads ``pixi.toml`` task definitions.

    Supports:
    - ``[tasks]`` top-level table
    - ``[target.<platform>.tasks]`` per-platform overrides
    """

    extensions: ClassVar[tuple[str, ...]] = (".toml",)
    filenames: ClassVar[tuple[str, ...]] = ("pixi.toml",)

    def can_handle(self, path: Path) -> bool:
        return path.name in self.filenames

    def parse(self, path: Path) -> dict[str, Task]:
        try:
            data = tomlkit.loads(path.read_text(encoding="utf-8")).unwrap()
        except Exception as exc:
            raise TaskParseError(str(path), str(exc)) from exc

        raw_tasks = data.get("tasks", {})
        if not isinstance(raw_tasks, dict):
            raise TaskParseError(str(path), "'tasks' must be a table")

        tasks: dict[str, Task] = {}
        for name, defn in raw_tasks.items():
            tasks[name] = normalize_task(name, defn)

        target = data.get("target", {})
        if isinstance(target, dict):
            for platform, platform_data in target.items():
                if not isinstance(platform_data, dict):
                    continue
                platform_tasks = platform_data.get("tasks", {})
                for name, defn in platform_tasks.items():
                    override = normalize_override(
                        defn if isinstance(defn, dict) else {"cmd": defn}
                    )
                    if name in tasks:
                        existing = tasks[name]
                        if existing.platforms is None:
                            existing.platforms = {}
                        existing.platforms[platform] = override
                    else:
                        task = normalize_task(name, defn)
                        task.platforms = {platform: override}
                        tasks[name] = task

        return tasks

    def add_task(self, path: Path, name: str, task: Task) -> None:
        raise NotImplementedError(
            "Writing to pixi.toml is not supported. Use conda-tasks.yml instead."
        )

    def remove_task(self, path: Path, name: str) -> None:
        raise NotImplementedError(
            "Writing to pixi.toml is not supported. Use conda-tasks.yml instead."
        )
