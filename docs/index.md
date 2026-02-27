# conda-tasks

Project-scoped task runner for conda, with pixi task compatibility.

Define tasks, wire up dependencies between them, and run everything through
`conda task`. conda-tasks reads `conda.toml`, `pixi.toml`, `pyproject.toml`,
or `.condarc` and runs commands in your existing conda environments — no new
package manager, no extra solver, just tasks on top of the tools you already
use.

## Install

::::{tab-set}

:::{tab-item} conda

```bash
conda install -c conda-forge conda-tasks
```

:::

:::{tab-item} pixi

```bash
pixi global install conda-tasks
```

:::

::::

## Define tasks

Create a `conda.toml` in your project root:

```toml
[tasks]
build = "python -m build"
test = { cmd = "pytest tests/ -v", depends-on = ["build"] }
lint = "ruff check ."

[tasks.check]
depends-on = ["test", "lint"]
```

Then run your tasks:

```bash
conda task run check    # resolves dependencies, runs build → lint → test
conda task run test     # builds first, then tests
conda task list         # shows all available tasks
```

Or use the `ct` shortcut for quicker typing:

```bash
ct run check
ct list
```

Tasks are executed in your current conda environment by default, or target
any environment with `-n myenv`. Dependencies are resolved with topological
ordering so everything runs in the right order.

## Why conda-tasks?

[pixi](https://pixi.sh) introduced an excellent task runner model, but it
brings its own environment management. conda-tasks reuses that same task
format while delegating execution to conda's existing infrastructure.

This means:

- Tasks read from `conda.toml`, `pixi.toml`, `pyproject.toml`, or
  `.condarc` — one definition, multiple tools
- Task dependencies with topological ordering (`depends-on`)
- Jinja2 templates in commands (`{{ conda.platform }}`, conditionals)
- Task arguments with defaults, input/output caching, and per-platform
  overrides
- Ships as a conda plugin (`conda task`) and a standalone `ct` CLI

Read more in [](motivation.md).

---

::::{grid} 2
:gutter: 3

:::{grid-item-card} {octicon}`rocket` Getting started
:link: quickstart
:link-type: doc

Install conda-tasks and define your first task in under a minute.
:::

:::{grid-item-card} {octicon}`mortar-board` Tutorials
:link: tutorials/index
:link-type: doc

Step-by-step guides: your first project, migrating from pixi, CI setup.
:::

:::{grid-item-card} {octicon}`list-unordered` Features
:link: features
:link-type: doc

Dependencies, templates, caching, arguments, platform overrides,
environment targeting, and more.
:::

:::{grid-item-card} {octicon}`gear` Configuration
:link: configuration
:link-type: doc

All task fields, file formats (`conda.toml`,
`pixi.toml`, `pyproject.toml`, `.condarc`), and examples.
:::

:::{grid-item-card} {octicon}`terminal` CLI reference
:link: reference/cli
:link-type: doc

Complete `conda task` command-line documentation.
:::

:::{grid-item-card} {octicon}`code` API reference
:link: reference/api
:link-type: doc

Python API for models, parsers, graph resolution, caching, and
template rendering.
:::

::::

```{toctree}
:hidden:

quickstart
tutorials/index
features
configuration
reference/cli
reference/api
motivation
changelog
```
