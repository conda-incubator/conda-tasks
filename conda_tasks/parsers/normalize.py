"""Shared logic for normalizing raw task dicts into Task model objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import Task, TaskArg, TaskDependency, TaskOverride

if TYPE_CHECKING:
    from typing import Any


def normalize_depends_on(raw: list[Any] | str | None) -> list[TaskDependency]:
    """Convert the various ``depends-on`` formats into TaskDependency objects.

    Accepted shapes:
    - ``["foo", "bar"]``  (simple list of task names)
    - ``[{"task": "foo", "args": ["x"]}, ...]``  (full dict form)
    - ``[{"task": "foo"}, {"task": "bar"}]``  (pixi alias shorthand)
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        return [TaskDependency(task=raw)]
    result: list[TaskDependency] = []
    for item in raw:
        if isinstance(item, str):
            result.append(TaskDependency(task=item))
        elif isinstance(item, dict):
            result.append(
                TaskDependency(
                    task=item["task"],
                    args=item.get("args", []),
                    environment=item.get("environment"),
                )
            )
    return result


def normalize_args(raw: list[Any] | None) -> list[TaskArg]:
    """Convert raw arg definitions into TaskArg objects.

    Accepted shapes:
    - ``["name"]``  (required arg, no default)
    - ``[{"arg": "name", "default": "value"}]``
    """
    if raw is None:
        return []
    result: list[TaskArg] = []
    for item in raw:
        if isinstance(item, str):
            result.append(TaskArg(name=item))
        elif isinstance(item, dict):
            result.append(TaskArg(name=item["arg"], default=item.get("default")))
    return result


def normalize_override(raw: dict[str, Any]) -> TaskOverride:
    """Parse a raw dict into a TaskOverride."""
    cmd = raw.get("cmd")
    return TaskOverride(
        cmd=cmd,
        args=normalize_args(raw.get("args")) or None,
        depends_on=normalize_depends_on(raw.get("depends-on", raw.get("depends_on")))
        or None,
        cwd=raw.get("cwd"),
        env=raw.get("env"),
        inputs=raw.get("inputs"),
        outputs=raw.get("outputs"),
        clean_env=raw.get("clean-env", raw.get("clean_env")),
    )


def normalize_task(name: str, raw: str | list[Any] | dict[str, Any]) -> Task:
    """Convert a single raw task value into a Task object.

    Handles all the shorthand forms:
    - ``"command string"``  (simple string command)
    - ``["dep1", "dep2"]`` or ``[{"task": ...}]`` (alias / dependency-only)
    - ``{cmd: ..., depends-on: ..., ...}`` (full dict definition)
    """
    if isinstance(raw, str):
        return Task(name=name, cmd=raw)

    if isinstance(raw, list):
        return Task(name=name, depends_on=normalize_depends_on(raw))

    cmd = raw.get("cmd")
    depends_raw = raw.get("depends-on", raw.get("depends_on"))
    env = raw.get("env", {})
    clean_env = raw.get("clean-env", raw.get("clean_env", False))
    default_env = raw.get("default-environment", raw.get("default_environment"))

    platforms: dict[str, TaskOverride] | None = None
    target_raw = raw.get("target")
    if target_raw and isinstance(target_raw, dict):
        platforms = {plat: normalize_override(ov) for plat, ov in target_raw.items()}

    return Task(
        name=name,
        cmd=cmd,
        args=normalize_args(raw.get("args")),
        depends_on=normalize_depends_on(depends_raw),
        cwd=raw.get("cwd"),
        env=env,
        description=raw.get("description"),
        inputs=raw.get("inputs", []),
        outputs=raw.get("outputs", []),
        clean_env=bool(clean_env),
        default_environment=default_env,
        platforms=platforms,
    )


def normalize_tasks(raw_tasks: dict[str, Any]) -> dict[str, Task]:
    """Convert a dict of ``{name: raw_definition}`` into ``{name: Task}``."""
    return {name: normalize_task(name, defn) for name, defn in raw_tasks.items()}
