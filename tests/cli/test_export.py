"""Tests for ``conda task export``."""

from __future__ import annotations

import argparse

from conda_tasks.cli.export import execute_export
from conda_tasks.parsers.toml import CondaTomlParser


def test_export_to_stdout(sample_yaml, capsys):
    args = argparse.Namespace(
        file=sample_yaml,
        output=None,
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute_export(args)
    assert result == 0
    output = capsys.readouterr().out
    assert "[tasks]" in output
    assert "build" in output
    assert "configure" in output


def test_export_to_file(sample_yaml, tmp_path):
    out_path = tmp_path / "exported.toml"
    args = argparse.Namespace(
        file=sample_yaml,
        output=out_path,
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute_export(args)
    assert result == 0
    assert out_path.exists()

    tasks = CondaTomlParser().parse(out_path)
    assert "build" in tasks
    assert "test" in tasks
    assert "lint" in tasks


def test_export_from_pixi_toml(tmp_path):
    """Export from pixi.toml produces valid conda.toml."""
    pixi = tmp_path / "pixi.toml"
    pixi.write_text(
        '[tasks]\nbuild = "make build"\n'
        'test = { cmd = "pytest", depends-on = ["build"] }\n'
        "\n[target.win-64.tasks]\n"
        'build = "nmake build"\n'
    )

    out_path = tmp_path / "conda.toml"
    args = argparse.Namespace(
        file=pixi,
        output=out_path,
        quiet=False,
        verbose=0,
        json=False,
        dry_run=False,
    )
    result = execute_export(args)
    assert result == 0

    tasks = CondaTomlParser().parse(out_path)
    assert "build" in tasks
    assert "test" in tasks
    assert tasks["test"].depends_on[0].task == "build"
    assert tasks["build"].platforms is not None
    assert "win-64" in tasks["build"].platforms
