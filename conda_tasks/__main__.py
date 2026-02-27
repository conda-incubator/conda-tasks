"""Standalone CLI entry point for ``ct`` (short for ``conda task``).

This module allows running conda-tasks without going through the
conda plugin dispatch::

    ct run test
    ct list
    ct add lint "ruff check ."

It reuses the same parser and execute logic as ``conda task``.
"""

from __future__ import annotations


def main(args: list[str] | None = None) -> None:
    """Entry point for the ``ct`` console script."""
    from .cli.main import execute, generate_parser

    parser = generate_parser()
    parser.prog = "ct"

    parsed = parser.parse_args(args)
    raise SystemExit(execute(parsed))


if __name__ == "__main__":
    main()
