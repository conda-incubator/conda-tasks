"""Handler for ``conda task remove``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import TaskParseError
from ..parsers import detect_and_parse, get_parser

if TYPE_CHECKING:
    import argparse


def execute_remove(args: argparse.Namespace) -> int:
    """Execute the ``conda task remove`` subcommand."""
    file_path = getattr(args, "file", None)
    task_file, tasks = detect_and_parse(file_path=file_path)

    parser = get_parser(task_file)
    if parser is None:
        raise TaskParseError(str(task_file), "no parser found for this file format")

    dry_run = getattr(args, "dry_run", False)
    quiet = getattr(args, "quiet", False)

    if dry_run:
        print(f"  [dry-run] Would remove task '{args.task_name}' from {task_file}")
        return 0

    parser.remove_task(task_file, args.task_name)
    if not quiet:
        print(f"  Removed task '{args.task_name}' from {task_file}")
    return 0
