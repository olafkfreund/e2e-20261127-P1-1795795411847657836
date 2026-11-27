# AC#3: main and `python -m wordfreq` read stdin by default; exit 0 or 2 with stderr.
# Verify `python -m wordfreq` as a subprocess reads stdin, emits TSV/JSON with a
# trailing newline, and exits 2 with stderr on a missing file.

import subprocess
import sys

import pytest

from wordfreq.cli import main  # noqa: F401  # import root per spec: target is wordfreq/cli.py::main


SAMPLE_TEXT = "the cat and the dog\n"


def _run_module(args, stdin_text, cwd):
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin_text,
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=60,
    )


@pytest.mark.parametrize(
    "args",
    [
        pytest.param([], id="default-tsv"),
        pytest.param(["--json"], id="json-flag"),
    ],
)
def test_python_m_wordfreq_stdin_default_exits_zero(args, tmp_path):
    result = _run_module(args, SAMPLE_TEXT, tmp_path)
    assert result.returncode == 0


@pytest.mark.parametrize(
    "args",
    [
        pytest.param([], id="default-tsv"),
        pytest.param(["--json"], id="json-flag"),
    ],
)
def test_python_m_wordfreq_stdin_output_ends_with_trailing_newline(args, tmp_path):
    result = _run_module(args, SAMPLE_TEXT, tmp_path)
    assert result.stdout.endswith("\n")


def test_python_m_wordfreq_missing_file_exits_two(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_module([str(missing)], "", tmp_path)
    assert result.returncode == 2


def test_python_m_wordfreq_missing_file_writes_stderr(tmp_path):
    missing = tmp_path / "does_not_exist.txt"
    result = _run_module([str(missing)], "", tmp_path)
    assert result.stderr.strip() != ""
