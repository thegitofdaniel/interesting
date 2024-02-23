import pytest

from src.interesting.utils import future_value, is_close, is_whole_number, present_value


@pytest.mark.parametrize(
    "a, b, expected_output",
    [
        (1.0, 1.0, True),  # exactly the same numbers
        (1.0, 1.0 + 1e-11, True),  # close due to epsilon
        (1.0, 1.00000000001, True),  # very close numbers
        (1.0, 1.1, False),  # not close numbers
        (1.0, 1.0 + 1e-9, False),  # not close due to epsilon
    ],
)
def test_is_close(a, b, expected_output):
    assert is_close(a, b) == expected_output


def test_future_value():
    assert future_value(present_value=1000, interest_rate=0.01, freqs=2) == 1020.1


def test_present_value():
    assert present_value(future_value=1020.1, interest_rate=0.01, freqs=2) == 1000


def test_is_whole_number():
    assert is_whole_number(1)
    assert is_whole_number(1.0)
    assert not is_whole_number(1.5)
