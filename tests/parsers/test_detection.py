"""Tests for parser detection and registry (conda_tasks.parsers.__init__)."""

from __future__ import annotations

import pytest

from conda_tasks.exceptions import NoTaskFileError
from conda_tasks.parsers import detect_and_parse, detect_task_file, get_parser
from conda_tasks.parsers.pixi_toml import PixiTomlParser
from conda_tasks.parsers.toml import CondaTomlParser


@pytest.mark.parametrize(
    ("fixture_name", "expected_filename"),
    [
        ("sample_conda_toml", "conda.toml"),
        ("sample_pixi_toml", "pixi.toml"),
    ],
)
def test_detect_task_file(fixture_name, expected_filename, request):
    path = request.getfixturevalue(fixture_name)
    found = detect_task_file(path.parent)
    assert found is not None
    assert found.name == expected_filename


def test_detect_priority_pixi_over_conda(
    tmp_project, sample_pixi_toml, sample_conda_toml
):
    """pixi.toml takes priority over conda.toml."""
    found = detect_task_file(tmp_project)
    assert found is not None
    assert found.name == "pixi.toml"


def test_detect_priority_conda_over_pyproject(
    tmp_project, sample_conda_toml, sample_pyproject
):
    """conda.toml takes priority over pyproject.toml."""
    found = detect_task_file(tmp_project)
    assert found is not None
    assert found.name == "conda.toml"


def test_detect_none(tmp_project):
    assert detect_task_file(tmp_project) is None


@pytest.mark.parametrize(
    ("fixture_name", "parser_class"),
    [
        ("sample_conda_toml", CondaTomlParser),
        ("sample_pixi_toml", PixiTomlParser),
    ],
)
def test_get_parser(fixture_name, parser_class, request):
    path = request.getfixturevalue(fixture_name)
    assert isinstance(get_parser(path), parser_class)


def test_get_parser_unknown(tmp_project):
    path = tmp_project / "unknown.xyz"
    path.write_text("data")
    assert get_parser(path) is None


def test_detect_and_parse_with_file(sample_yaml):
    path, tasks = detect_and_parse(file_path=sample_yaml)
    assert path == sample_yaml.resolve()
    assert "build" in tasks


def test_detect_and_parse_no_file(tmp_path):
    with pytest.raises(NoTaskFileError):
        detect_and_parse(start_dir=tmp_path)
