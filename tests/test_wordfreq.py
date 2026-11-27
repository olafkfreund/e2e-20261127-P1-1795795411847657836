"""Unit and CLI tests for the wordfreq package."""

from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from wordfreq.cli import count_words, format_table, main

REPO_ROOT = Path(__file__).resolve().parent.parent


def _run_module(*args: str, stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    """Run `python -m wordfreq` in a subprocess and capture its raw output."""
    return subprocess.run(
        [sys.executable, "-m", "wordfreq", *args],
        input=stdin,
        capture_output=True,
        cwd=REPO_ROOT,
        check=False,
    )


def test_count_words_basic_ranking() -> None:
    text = "Apple banana apple, cherry! Banana apple."
    assert count_words(text) == [("apple", 3), ("banana", 2), ("cherry", 1)]


def test_format_table_tsv() -> None:
    assert format_table([("apple", 3), ("banana", 2)]) == "apple\t3\nbanana\t2"


def test_cli_top_and_min_len(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("to be or not to be that is the question", encoding="utf-8")
    rc = main([str(sample), "--min-len", "3", "--top", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.strip().splitlines() == ["not\t1", "question\t1"]


# --- count_words: ranking and tie-breaking -------------------------------------


def test_count_words_breaks_ties_alphabetically() -> None:
    assert count_words("pear fig apple fig pear kiwi") == [
        ("fig", 2),
        ("pear", 2),
        ("apple", 1),
        ("kiwi", 1),
    ]


def test_count_words_tie_order_is_independent_of_input_order() -> None:
    forward = count_words("zeta alpha mid")
    backward = count_words("mid alpha zeta")
    assert forward == backward == [("alpha", 1), ("mid", 1), ("zeta", 1)]


def test_count_words_empty_text_returns_empty_list() -> None:
    assert count_words("") == []


def test_count_words_top_limits_results_after_sorting() -> None:
    assert count_words("c b b a a a", top=2) == [("a", 3), ("b", 2)]


def test_count_words_top_zero_returns_empty_list() -> None:
    assert count_words("a b", top=0) == []


# --- count_words: tokenisation and case handling -------------------------------


def test_count_words_only_counts_ascii_alphanumeric_runs() -> None:
    assert count_words("foo_bar don't café 42 42") == [
        ("42", 2),
        ("bar", 1),
        ("caf", 1),
        ("don", 1),
        ("foo", 1),
        ("t", 1),
    ]


def test_count_words_lowercases_by_default() -> None:
    assert count_words("Apple APPLE apple") == [("apple", 3)]


def test_count_words_preserves_case_when_ignore_case_is_false() -> None:
    assert count_words("Apple APPLE apple", ignore_case=False) == [
        ("APPLE", 1),
        ("Apple", 1),
        ("apple", 1),
    ]


def test_count_words_filters_by_min_len() -> None:
    assert count_words("a bb ccc bb a", min_len=2) == [("bb", 2), ("ccc", 1)]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"min_len": 0}, "min_len must be >= 1"),
        ({"min_len": -3}, "min_len must be >= 1"),
        ({"top": -1}, "top must be >= 0"),
    ],
)
def test_count_words_rejects_invalid_arguments(
    kwargs: dict[str, int], message: str
) -> None:
    with pytest.raises(ValueError, match=re.escape(message)):
        count_words("a", **kwargs)


# --- format_table ---------------------------------------------------------------


def test_format_table_empty_input_returns_empty_string() -> None:
    assert format_table([]) == ""


def test_format_table_has_no_trailing_newline() -> None:
    assert not format_table([("a", 1)]).endswith("\n")


# --- main: input sources --------------------------------------------------------


def test_main_reads_stdin_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stdin = io.TextIOWrapper(io.BytesIO(b"one two two\n"), encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", stdin)
    assert main([]) == 0
    assert capsys.readouterr().out == "two\t2\none\t1\n"


def test_main_dash_path_reads_stdin(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stdin = io.TextIOWrapper(io.BytesIO(b"one two two\n"), encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", stdin)
    assert main(["-"]) == 0
    assert capsys.readouterr().out == "two\t2\none\t1\n"


def test_main_reads_stdin_text_when_buffer_is_unavailable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO("hi hi\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "hi\t2\n"


def test_main_reads_positional_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("beta alpha beta\n", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "beta\t2\nalpha\t1\n"


# --- main: options --------------------------------------------------------------


def test_main_case_sensitive_keeps_original_case(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Apple apple\n", encoding="utf-8")
    assert main([str(sample), "--case-sensitive"]) == 0
    assert capsys.readouterr().out == "Apple\t1\napple\t1\n"


def test_main_default_lowercases_and_merges_case(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("Apple apple\n", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "apple\t2\n"


def test_main_tie_order_is_alphabetical(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("pear fig apple fig pear kiwi\n", encoding="utf-8")
    assert main([str(sample)]) == 0
    assert capsys.readouterr().out == "fig\t2\npear\t2\napple\t1\nkiwi\t1\n"


# --- main: output formatting ----------------------------------------------------


def test_main_tsv_output_ends_with_single_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("beta alpha beta\n", encoding="utf-8")
    assert main([str(sample)]) == 0
    out = capsys.readouterr().out
    assert out == "beta\t2\nalpha\t1\n"
    assert out.endswith("\n")
    assert not out.endswith("\n\n")


def test_main_empty_tsv_output_writes_nothing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main([]) == 0
    assert capsys.readouterr().out == ""


def test_main_min_len_filtering_everything_writes_nothing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("a b c\n", encoding="utf-8")
    assert main([str(sample), "--min-len", "9"]) == 0
    assert capsys.readouterr().out == ""


def test_main_json_output_is_array_with_trailing_newline(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("beta alpha beta\n", encoding="utf-8")
    assert main([str(sample), "--json"]) == 0
    out = capsys.readouterr().out
    assert out == '[{"word": "beta", "count": 2}, {"word": "alpha", "count": 1}]\n'
    assert out.endswith("\n")
    assert not out.endswith("\n\n")
    assert json.loads(out) == [
        {"word": "beta", "count": 2},
        {"word": "alpha", "count": 1},
    ]


def test_main_json_empty_input_prints_empty_array(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    assert main(["--json"]) == 0
    assert capsys.readouterr().out == "[]\n"


# --- main: invalid arguments and missing files ----------------------------------


@pytest.mark.parametrize(
    "argv",
    [
        ["--top", "-1"],
        ["--top", "abc"],
        ["--min-len", "0"],
        ["--min-len", "x"],
        ["--unknown"],
    ],
)
def test_main_rejects_invalid_arguments_with_exit_code_2(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(argv) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


def test_main_missing_file_returns_2_with_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    missing = tmp_path / "missing.txt"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing.txt" in captured.err


def test_main_non_utf8_file_returns_2_with_stderr(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    binary = tmp_path / "binary.txt"
    binary.write_bytes(b"\xff\xfe\xfa")
    assert main([str(binary)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err != ""


# --- python -m wordfreq ---------------------------------------------------------


def test_module_reads_stdin_by_default() -> None:
    result = _run_module(stdin=b"one two two\n")
    assert result.returncode == 0
    assert result.stdout == b"two\t2\none\t1\n"
    assert result.stderr == b""


def test_module_dash_path_reads_stdin() -> None:
    result = _run_module("-", stdin=b"x\n")
    assert result.returncode == 0
    assert result.stdout == b"x\t1\n"


def test_module_empty_input_writes_nothing() -> None:
    result = _run_module(stdin=b"")
    assert result.returncode == 0
    assert result.stdout == b""


def test_module_json_output_with_trailing_newline() -> None:
    result = _run_module("--json", "--case-sensitive", stdin=b"Ab ab\n")
    assert result.returncode == 0
    assert (
        result.stdout == b'[{"word": "Ab", "count": 1}, {"word": "ab", "count": 1}]\n'
    )


def test_module_missing_file_exits_2_with_stderr(tmp_path: Path) -> None:
    result = _run_module(str(tmp_path / "missing.txt"))
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr != b""


def test_module_invalid_argument_exits_2_with_stderr() -> None:
    result = _run_module("--top", "-1", stdin=b"a\n")
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr != b""
