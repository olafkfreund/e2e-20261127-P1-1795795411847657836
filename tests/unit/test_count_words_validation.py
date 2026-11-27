# Criterion (AC#1): count_words filters by min_len, truncates by top, and raises
# ValueError('min_len must be >= 1') / ValueError('top must be >= 0').

import pytest

from wordfreq.cli import count_words


TEXT = "a bb ccc dddd eeeee the the the cat cat dog"


def _words(result):
    """Return the set of words from a count_words result (dict or list of pairs)."""
    if isinstance(result, dict):
        return set(result.keys())
    return {item[0] for item in result}


@pytest.fixture
def sample_text():
    return TEXT


@pytest.mark.parametrize(
    "min_len,excluded",
    [
        (2, {"a"}),
        (3, {"a", "bb"}),
        (4, {"a", "bb", "ccc"}),
        (5, {"a", "bb", "ccc", "dddd"}),
    ],
    ids=["min_len_2_drops_1_char", "min_len_3_drops_up_to_2_chars",
         "min_len_4_drops_up_to_3_chars", "min_len_5_drops_up_to_4_chars"],
)
def test_count_words_min_len_filter_excludes_short_words(sample_text, min_len, excluded):
    result = count_words(sample_text, min_len=min_len)

    words = _words(result)
    assert words.isdisjoint(excluded)


@pytest.mark.parametrize(
    "min_len,kept",
    [
        (3, {"ccc", "dddd", "eeeee", "the"}),
        (5, {"eeeee"}),
    ],
    ids=["min_len_3_keeps_words_of_length_3_or_more", "min_len_5_keeps_only_length_5"],
)
def test_count_words_min_len_filter_keeps_long_words(sample_text, min_len, kept):
    result = count_words(sample_text, min_len=min_len)

    assert kept <= _words(result)


@pytest.mark.parametrize(
    "top,expected_count",
    [
        (1, 1),
        (2, 2),
        (3, 3),
    ],
    ids=["top_1_returns_one_word", "top_2_returns_two_words", "top_3_returns_three_words"],
)
def test_count_words_top_truncates_result_to_top_entries(sample_text, top, expected_count):
    result = count_words(sample_text, top=top)

    assert len(_words(result)) == expected_count


def test_count_words_top_zero_returns_no_words_empty(sample_text):
    result = count_words(sample_text, top=0)

    assert len(_words(result)) == 0


def test_count_words_min_len_zero_raises_value_error_exact_message(sample_text):
    with pytest.raises(ValueError) as exc_info:
        count_words(sample_text, min_len=0)

    assert str(exc_info.value) == "min_len must be >= 1"


def test_count_words_min_len_negative_raises_value_error_exact_message(sample_text):
    with pytest.raises(ValueError) as exc_info:
        count_words(sample_text, min_len=-1)

    assert str(exc_info.value) == "min_len must be >= 1"


def test_count_words_top_negative_raises_value_error_exact_message(sample_text):
    with pytest.raises(ValueError) as exc_info:
        count_words(sample_text, top=-1)

    assert str(exc_info.value) == "top must be >= 0"
