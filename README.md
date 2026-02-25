# conda-tasks

Pixi-style task runner plugin for conda.

## Overview

`conda-tasks` adds a `conda task` subcommand that brings pixi's powerful task
runner system to conda. Define tasks in `conda-tasks.yml`, `pixi.toml`,
`pyproject.toml`, or `.condarc`, then run them with `conda task run <name>`.

## Features

- Multiple file formats: `conda-tasks.yml` (canonical), `pixi.toml`,
  `pyproject.toml`, `.condarc`
- Dependency graphs: tasks can depend on other tasks with topological ordering
- Jinja2 templates: use `{{ conda.platform }}` and other variables in commands
- Task arguments: pass arguments to tasks with defaults
- Caching: skip re-execution when inputs haven't changed
- Cross-platform: per-platform task overrides for OS-specific commands
- Conda environments: run tasks in specific conda environments

## Installation

```bash
conda install conda-tasks
```

## Quick Start

Create a `conda-tasks.yml` in your project root:

```yaml
tasks:
  build:
    cmd: "python -m build"
    description: "Build the package"
  test:
    cmd: "pytest tests/"
    depends-on: [build]
    description: "Run tests"
```

Run a task:

```bash
conda task run test
conda task list
```

## Documentation

Full documentation is available at https://jezdez.github.io/conda-tasks/.
