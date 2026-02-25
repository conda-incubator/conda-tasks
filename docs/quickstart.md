# Quick start

## Installation

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

## Your first task file

Create a task file in your project root:

::::{tab-set}

:::{tab-item} conda-tasks.yml

```yaml
tasks:
  hello:
    cmd: "echo Hello from conda-tasks!"
    description: "A simple hello world task"
```

:::

:::{tab-item} conda-tasks.toml

```toml
[tasks]
hello = { cmd = "echo Hello from conda-tasks!", description = "A simple hello world task" }
```

:::

::::

Run it:

```bash
conda task run hello
```

## Task dependencies

Tasks can depend on other tasks:

::::{tab-set}

:::{tab-item} conda-tasks.yml

```yaml
tasks:
  compile:
    cmd: "gcc -o main main.c"
    description: "Compile the program"
  test:
    cmd: "./main --test"
    depends-on: [compile]
    description: "Run tests"
```

:::

:::{tab-item} conda-tasks.toml

```toml
[tasks]
compile = { cmd = "gcc -o main main.c", description = "Compile the program" }
test = { cmd = "./main --test", depends-on = ["compile"], description = "Run tests" }
```

:::

::::

Running `conda task run test` will first run `compile`, then `test`.

## Listing tasks

```bash
conda task list
```

## Supported file formats

conda-tasks automatically detects task definitions from these files (in order):

1. `conda-tasks.yml` -- canonical YAML format
2. `conda-tasks.toml` -- canonical TOML format (same structure as pixi.toml)
3. `pixi.toml` -- reads the `[tasks]` table directly
4. `pyproject.toml` -- reads `[tool.conda-tasks.tasks]` or `[tool.pixi.tasks]`
5. `.condarc` -- reads `plugins.conda_tasks.tasks` (via conda's settings API)

## Running in a specific environment

```bash
conda task run test -n myenv
```

This activates `myenv` before running the task, just like `conda run -n myenv`.

## Next steps

::::{grid} 2
:gutter: 3

:::{grid-item-card} {octicon}`mortar-board` Your first project
:link: tutorials/first-project
:link-type: doc

A full walkthrough: build, test, lint, cache, and platform overrides.
:::

:::{grid-item-card} {octicon}`arrow-switch` Coming from pixi?
:link: tutorials/coming-from-pixi
:link-type: doc

What's the same, what's different, and how to migrate.
:::

::::
