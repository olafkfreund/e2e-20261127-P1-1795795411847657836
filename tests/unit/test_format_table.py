# AC#2: format_table formats rows as word\tcount lines separated by \n and returns '' for empty input

import pytest

from wordfreq.cli import format_table


@pytest.mark.parametrize(
    "rows,expected",
    [
        ([("apple", 3)], "apple\t3"),
        ([("apple", 3), ("banana", 1)], "apple\t3\nbanana\t1"),
        ([("a", 10), ("b", 2), ("c", 1)], "a\t10\nb\t2\nc\t1"),
    ],
    ids=["single_row", "two_rows", "three_rows"],
)
def test_format_table_rows_joined_as_tab_separated_lines(rows, expected):
    assert format_table(rows) == expected


def test_format_table_rows_no_trailing_newline():
    rows = [("apple", 3), ("banana", 1)]
    assert not format_table(rows).endswith("\n")


def test_format_table_empty_input_returns_empty_string():
    assert format_table([]) == ""
