"""Tests for conda_tasks.parsers.pyproject_toml."""

from __future__ import annotations

import pytest

from conda_tasks.models import Task
from conda_tasks.parsers.pyproject_toml import PyprojectTomlParser


def test_can_handle(sample_pyproject):
    assert PyprojectTomlParser().can_handle(sample_pyproject)


def test_can_handle_no_tasks(tmp_project):
    path = tmp_project / "pyproject.toml"
    path.write_text('[project]\nname = "example"\n')
    assert not PyprojectTomlParser().can_handle(path)


@pytest.mark.parametrize("task_name", ["build", "test"])
def test_parse_contains_task(sample_pyproject, task_name):
    tasks = PyprojectTomlParser().parse(sample_pyproject)
    assert task_name in tasks


@pytest.mark.parametrize(
    ("task_name", "attr", "expected"),
    [
        ("build", "cmd", "make build"),
    ],
)
def test_parse_task_attr(sample_pyproject, task_name, attr, expected):
    tasks = PyprojectTomlParser().parse(sample_pyproject)
    assert getattr(tasks[task_name], attr) == expected


def test_parse_depends(sample_pyproject):
    tasks = PyprojectTomlParser().parse(sample_pyproject)
    assert tasks["test"].depends_on[0].task == "build"


def test_platform_override(sample_pyproject):
    tasks = PyprojectTomlParser().parse(sample_pyproject)
    assert tasks["build"].platforms is not None
    assert "win-64" in tasks["build"].platforms


def test_pixi_fallback(tmp_project):
    path = tmp_project / "pyproject.toml"
    path.write_text(
        '[project]\nname = "example"\n\n[tool.pixi.tasks]\nbuild = "make"\n'
    )
    parser = PyprojectTomlParser()
    assert parser.can_handle(path)
    tasks = parser.parse(path)
    assert "build" in tasks


def test_parse_target_only_task(tmp_project):
    content = (
        '[project]\nname = "x"\n\n'
        "[tool.conda-tasks.tasks]\n"
        'build = "make"\n\n'
        "[tool.conda-tasks.target.win-64.tasks]\n"
        'special = "win-cmd"\n'
    )
    path = tmp_project / "pyproject.toml"
    path.write_text(content)
    tasks = PyprojectTomlParser().parse(path)
    assert "special" in tasks
    assert tasks["special"].platforms is not None


@pytest.mark.parametrize(
    "method, args",
    [
        ("add_task", lambda p: (p, "x", Task(name="x", cmd="echo"))),
        ("remove_task", lambda p: (p, "build")),
    ],
)
def test_write_raises(sample_pyproject, method, args):
    with pytest.raises(NotImplementedError):
        getattr(PyprojectTomlParser(), method)(*args(sample_pyproject))
