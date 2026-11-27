# AC#3: main reads stdin by default, honors options, terminates output with final newline, returns 0
# Subtask: main-stdin-options-output
import io
import json

import pytest

from wordfreq.cli import main


@pytest.fixture
def feed_stdin(monkeypatch):
    def _feed(text):
        monkeypatch.setattr("sys.stdin", io.StringIO(text))

    return _feed


def test_main_no_args_reads_stdin_returns_zero(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")
    assert main([]) == 0


def test_main_no_args_reads_stdin_outputs_words(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")
    main([])
    assert "apple" in capsys.readouterr().out


def test_main_dash_arg_reads_stdin_returns_zero(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")
    assert main(["-"]) == 0


def test_main_dash_arg_reads_stdin_outputs_words(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")
    main(["-"])
    assert "banana" in capsys.readouterr().out


def test_main_default_case_folds_words_excludes_capitalized_form(feed_stdin, capsys):
    feed_stdin("Apple apple\n")
    main([])
    assert "Apple" not in capsys.readouterr().out


def test_main_case_sensitive_flag_keeps_capitalized_form(feed_stdin, capsys):
    feed_stdin("Apple apple\n")
    main(["--case-sensitive"])
    assert "Apple" in capsys.readouterr().out


def test_main_top_option_limits_output_to_one_line(feed_stdin, capsys):
    feed_stdin("apple apple apple banana banana cherry\n")
    main(["--top", "1"])
    lines = [line for line in capsys.readouterr().out.splitlines() if line.strip()]
    assert len(lines) == 1


def test_main_min_len_option_excludes_short_words(feed_stdin, capsys):
    feed_stdin("a bb ccc dddd\n")
    main(["--min-len", "3"])
    out = capsys.readouterr().out
    words = {line.split("\t")[0].strip() for line in out.splitlines() if line.strip()}
    assert "a" not in words and "bb" not in words


def test_main_tsv_output_ends_with_newline(feed_stdin, capsys):
    feed_stdin("apple banana\n")
    main([])
    out = capsys.readouterr().out
    assert out.endswith("\n")


def test_main_tsv_output_is_non_empty_for_nonempty_input(feed_stdin, capsys):
    feed_stdin("apple banana\n")
    main([])
    assert capsys.readouterr().out != ""


def test_main_json_output_is_valid_json(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")
    main(["--json"])
    json.loads(capsys.readouterr().out)


def test_main_json_output_ends_with_newline(feed_stdin, capsys):
    feed_stdin("apple apple banana\n")
    main(["--json"])
    assert capsys.readouterr().out.endswith("\n")


def test_main_empty_tsv_input_writes_nothing(feed_stdin, capsys):
    feed_stdin("")
    main([])
    assert capsys.readouterr().out == ""


def test_main_empty_tsv_input_returns_zero(feed_stdin, capsys):
    feed_stdin("")
    assert main([]) == 0
