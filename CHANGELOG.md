# Changelog

## Unreleased

## 0.1.0 — 2026-03-05

- Initial implementation of `conda task` subcommand
- Support for `pixi.toml`, `conda.toml`, `pyproject.toml`, and `.condarc`
- Task dependency graphs with topological sorting
- Jinja2 template rendering with `conda.*` context variables
- Task argument system with defaults
- File-based caching with inputs/outputs fingerprinting
- Platform-specific task overrides
- Conda environment activation for task execution
- `conda task run`, `list`, `add`, `remove` subcommands
- PyPI release workflow with trusted publishing
