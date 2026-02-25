"""Handler for ``conda task list``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..parsers import detect_and_parse

if TYPE_CHECKING:
    import argparse


def execute_list(args: argparse.Namespace) -> int:
    """Execute the ``conda task list`` subcommand."""
    file_path = getattr(args, "file", None)
    task_file, tasks = detect_and_parse(file_path=file_path)

    use_json = getattr(args, "json", False)

    visible_tasks = {name: t for name, t in sorted(tasks.items()) if not t.is_hidden}

    if use_json:
        from conda.common.io import stdout_json

        data: dict[str, dict[str, object]] = {}
        for name, task in visible_tasks.items():
            entry: dict[str, object] = {"name": name}
            if task.cmd is not None:
                entry["cmd"] = task.cmd
            if task.description:
                entry["description"] = task.description
            if task.depends_on:
                entry["depends_on"] = [d.task for d in task.depends_on]
            if task.is_alias:
                entry["alias"] = True
            data[name] = entry

        stdout_json({"tasks": data, "file": str(task_file)})
        return 0

    if not visible_tasks:
        print(f"No tasks defined in {task_file}")
        return 0

    print(f"Tasks from {task_file}:\n")

    name_width = max(len(n) for n in visible_tasks)
    for name, task in visible_tasks.items():
        desc = task.description or task.cmd or "(alias)"
        if isinstance(desc, list):
            desc = " ".join(desc)
        deps = ""
        if task.depends_on:
            dep_names = ", ".join(d.task for d in task.depends_on)
            deps = f"  [depends: {dep_names}]"
        print(f"  {name:<{name_width}}  {desc}{deps}")

    return 0
