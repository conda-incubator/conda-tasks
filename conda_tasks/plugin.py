"""Conda plugin registration for conda-tasks.

This module is imported on *every* conda invocation via the entry point
system.  Only ``hookimpl`` and ``CondaSubcommand`` are imported at module
level -- everything else is lazily imported inside the hook to keep the
overhead under 1 ms.
"""

from conda.plugins import hookimpl
from conda.plugins.types import CondaSubcommand


@hookimpl
def conda_subcommands():
    from .cli import configure_parser, execute

    yield CondaSubcommand(
        name="task",
        summary="Run, list, and manage project tasks.",
        action=execute,  # ty: ignore[invalid-argument-type]
        configure_parser=configure_parser,
    )


@hookimpl
def conda_settings():
    from conda.common.configuration import MapParameter, PrimitiveParameter
    from conda.plugins.types import CondaSetting

    yield CondaSetting(
        name="conda_tasks",
        description="Task definitions for the conda-tasks plugin.",
        parameter=MapParameter(PrimitiveParameter("", element_type=str)),
        aliases=("conda-tasks",),
    )
