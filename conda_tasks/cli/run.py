"""Handler for ``conda task run``."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from conda.base.context import context, locate_prefix_by_name

from ..cache import is_cached, save_cache
from ..exceptions import CondaTasksError, TaskExecutionError
from ..graph import resolve_execution_order
from ..parsers import detect_and_parse
from ..runner import SubprocessShell
from ..template import render, render_list

if TYPE_CHECKING:
    import argparse

    from ..models import Task


def _resolve_conda_prefix(args: argparse.Namespace) -> Path | None:
    """Determine the target conda prefix from CLI flags or conda context."""
    prefix = getattr(args, "prefix", None)
    name = getattr(args, "name", None)

    if prefix:
        return Path(prefix)
    if name:
        return Path(locate_prefix_by_name(name))

    if context.target_prefix:
        return Path(context.target_prefix)
    return None


def _resolve_task_args(task: Task, cli_args: list[str]) -> dict[str, str]:
    """Map positional CLI arguments to named task arguments."""
    result: dict[str, str] = {}
    for i, task_arg in enumerate(task.args):
        if i < len(cli_args):
            result[task_arg.name] = cli_args[i]
        elif task_arg.default is not None:
            result[task_arg.name] = task_arg.default
        else:
            raise CondaTasksError(
                f"Missing required argument '{task_arg.name}' for task '{task.name}'"
            )
    return result


def execute_run(args: argparse.Namespace) -> int:
    """Execute the ``conda task run`` subcommand."""
    file_path = getattr(args, "file", None)
    task_file, tasks = detect_and_parse(file_path=file_path)
    project_root = task_file.parent

    subdir = context.subdir
    tasks = {name: t.resolve_for_platform(subdir) for name, t in tasks.items()}

    target_name = args.task_name
    order = resolve_execution_order(
        target_name,
        tasks,
        skip_deps=args.skip_deps,
    )

    dry_run = getattr(args, "dry_run", False)
    quiet = getattr(args, "quiet", False)
    verbose = getattr(args, "verbose", 0) or 0
    conda_prefix = _resolve_conda_prefix(args)

    task_args = _resolve_task_args(tasks[target_name], args.task_args)

    shell = SubprocessShell()

    for name in order:
        task = tasks[name]

        if task.is_alias:
            continue

        if name == target_name:
            current_args = task_args
        else:
            dep_info = next(
                (d for d in tasks[target_name].depends_on if d.task == name),
                None,
            )
            current_args = {}
            if dep_info and dep_info.args:
                for i, da in enumerate(dep_info.args):
                    if isinstance(da, dict):
                        current_args.update(da)
                    elif i < len(task.args):
                        current_args[task.args[i].name] = render(
                            da,
                            manifest_path=task_file,
                            task_args=task_args,
                        )

        cmd = task.cmd
        if cmd is None:
            continue
        if isinstance(cmd, list):
            cmd = " ".join(cmd)

        cmd = render(cmd, manifest_path=task_file, task_args=current_args)

        task_env = {
            k: render(v, manifest_path=task_file, task_args=current_args)
            for k, v in task.env.items()
        }

        cwd = Path(args.cwd) if args.cwd else Path(task.cwd or project_root)
        clean_env = args.clean_env or task.clean_env

        task_prefix = conda_prefix
        if task.default_environment and not (
            getattr(args, "prefix", None) or getattr(args, "name", None)
        ):
            task_prefix = Path(locate_prefix_by_name(task.default_environment))

        rendered_inputs = render_list(
            task.inputs, manifest_path=task_file, task_args=current_args
        )
        rendered_outputs = render_list(
            task.outputs, manifest_path=task_file, task_args=current_args
        )

        if rendered_inputs or rendered_outputs:
            if is_cached(
                project_root,
                name,
                cmd,
                task_env,
                rendered_inputs,
                rendered_outputs,
                cwd,
            ):
                if not quiet:
                    print(f"  [cached] {name}")
                continue

        if dry_run:
            print(f"  [dry-run] {name}: {cmd}")
            continue

        if not quiet:
            print(f"  [run] {name}: {cmd}")

        if verbose and (rendered_inputs or rendered_outputs):
            if rendered_inputs:
                print(f"    inputs: {rendered_inputs}")
            if rendered_outputs:
                print(f"    outputs: {rendered_outputs}")

        exit_code = shell.run(
            cmd,
            task_env,
            cwd,
            conda_prefix=task_prefix,
            clean_env=clean_env,
        )

        if exit_code != 0:
            raise TaskExecutionError(name, exit_code)

        if rendered_inputs or rendered_outputs:
            save_cache(
                project_root,
                name,
                cmd,
                task_env,
                rendered_inputs,
                rendered_outputs,
                cwd,
            )

    return 0
