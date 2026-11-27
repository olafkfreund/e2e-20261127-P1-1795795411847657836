# AC#4: pytest -q passes across tests/test_wordfreq.py
# Criterion: the argparse type converter wordfreq/cli.py::_int_at_least must
# be exercised through the parser; the suite must pass.
# Target: wordfreq.cli._int_at_least (argparse `type=` converter).

import argparse

import pytest

from wordfreq.cli import _int_at_least


@pytest.fixture
def parser():
    p = argparse.ArgumentParser(prog="wordfreq")
    p.add_argument("--count", type=_int_at_least(1))
    return p


@pytest.mark.parametrize(
    "raw,expected",
    [("1", 1), ("5", 5), ("100", 100)],
    ids=["minimum", "small", "large"],
)
def test_int_at_least_valid_value_parsed_through_parser_returns_int(parser, raw, expected):
    args = parser.parse_args(["--count", raw])
    assert args.count == expected


@pytest.mark.parametrize(
    "raw",
    ["0", "-1", "-100"],
    ids=["zero", "negative_one", "negative_large"],
)
def test_int_at_least_below_minimum_through_parser_exits(parser, raw, capsys):
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--count", raw])
    assert excinfo.value.code == 2
    assert "--count" in capsys.readouterr().err


@pytest.mark.parametrize(
    "raw",
    ["abc", "1.5", ""],
    ids=["alpha", "float", "empty"],
)
def test_int_at_least_non_integer_through_parser_exits(parser, raw, capsys):
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--count", raw])
    assert excinfo.value.code == 2
    assert "--count" in capsys.readouterr().err
