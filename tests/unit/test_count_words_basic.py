# AC#1: count_words extracts tokens, lowercases by default, preserves case when
# ignore_case=False, sorts by (-count, word).

import pytest

from wordfreq.cli import count_words


def test_count_words_extracts_alphanumeric_tokens_only():
    result = count_words("abc 123 def-ghi")

    assert {word for word, _ in result} == {"abc", "123", "def", "ghi"}


@pytest.mark.parametrize(
    "text,expected_words",
    [
        ("hello, world!", {"hello", "world"}),
        ("a.b;c:d", {"a", "b", "c", "d"}),
        ("x1 y2 z3", {"x1", "y2", "z3"}),
    ],
    ids=["comma-and-bang", "semicolon-colon-dot", "digits-attached"],
)
def test_count_words_punctuation_splits_tokens(text, expected_words):
    result = count_words(text)

    assert {word for word, _ in result} == expected_words


def test_count_words_lowercases_by_default():
    result = count_words("Apple APPLE apple")

    assert result == [("apple", 3)]


def test_count_words_preserves_case_when_ignore_case_false():
    result = count_words("Apple APPLE apple", ignore_case=False)

    assert sorted(result) == sorted([("Apple", 1), ("APPLE", 1), ("apple", 1)])


def test_count_words_sorts_by_count_descending():
    result = count_words("b a b c a b")

    assert result == [("b", 3), ("a", 2), ("c", 1)]


def test_count_words_breaks_ties_alphabetically():
    result = count_words("zeta alpha mid")

    assert result == [("alpha", 1), ("mid", 1), ("zeta", 1)]
