from datetime import datetime

import pytest

from src.interesting.time import (
    calculate_delta_months,
    calculate_delta_years,
    datetime_to_string,
    generate_monthly_date_range,
    generate_yearly_date_range,
    is_last_day_of_month,
    is_leap_year,
    last_date_in_next_month,
    same_or_last_date_in_next_month,
    string_to_datetime,
)


@pytest.mark.parametrize(
    "year, expected",
    [
        (2000, True),  # 2000 is a leap year
        (1900, False),  # 1900 is not a leap year
        (2004, True),  # 2004 is a leap year
        (2001, False),  # 2001 is not a leap year
        (1800, False),  # 1800 is not a leap year
        (2000000, True),  # A very large leap year
        (0, True),  # Year 0 is considered a leap year in this context
        (2400, True),  # 2400 is a leap year
    ],
)
def test_is_leap_year(year, expected):
    assert is_leap_year(year) == expected


@pytest.mark.parametrize(
    "start_date, end_date, expected_result",
    [
        (datetime(2020, 1, 1), datetime(2025, 1, 1), 5.0),
        (datetime(2020, 1, 1), datetime(2025, 6, 30), 5.5),
        (datetime(2023, 12, 1), datetime(2030, 12, 1), 7.0),
        (datetime(2023, 12, 1), datetime(2024, 12, 1), 1.0),
        (datetime(2023, 12, 1), datetime(2024, 12, 1), 1.0),
        (datetime(2022, 1, 1), datetime(2023, 1, 1), 1.0),
        (datetime(2022, 1, 1), datetime(2022, 7, 1), 0.5),
        (datetime(2022, 1, 1), datetime(2028, 1, 1), 6.0),
        (datetime(2022, 1, 31), datetime(2023, 7, 30), 1.5),
        (datetime(2022, 1, 31), datetime(2023, 7, 31), 1.5),
    ],
)
def test_calculate_delta_years(start_date, end_date, expected_result):
    result = calculate_delta_years(start_date, end_date)
    assert abs(result - expected_result) <= 1e-2


@pytest.mark.parametrize(
    "date_to_check, expected_result",
    [
        (datetime(2023, 1, 31), True),  # Last day of the month
        (datetime(2023, 2, 28), True),  # Last day of the month (not leap year)
        (datetime(2023, 2, 27), False),  # Not the last day of the month (not leap year)
        (datetime(2023, 12, 31), True),  # Last day of the year
        (datetime(2024, 2, 29), True),  # Last day of the month (leap year)
        (datetime(2024, 2, 28), False),  # Not the last day of the month (leap year)
        (datetime(2024, 12, 31), True),  # Last day of the year (leap year)
    ],
)
def test_is_last_day_of_month(date_to_check, expected_result):
    assert is_last_day_of_month(date_to_check) == expected_result


@pytest.mark.parametrize(
    "start_date, end_date, expected_output",
    [
        ("2022-01-01", "2022-12-31", 12),  # XXX does it make sense?
        ("2021-01-01", "2022-01-01", 12),
        ("2022-01-01", "2022-01-01", 0),
        ("2020-02-29", "2020-06-30", 4),
    ],
)
def test_calculate_delta_months(start_date, end_date, expected_output):
    assert (
        calculate_delta_months(
            string_to_datetime(start_date), string_to_datetime(end_date)
        )
        == expected_output
    )


def test_generate_yearly_date_range():
    result = generate_yearly_date_range(
        start_date=datetime(2024, 1, 10), end_date=datetime(2029, 1, 10)
    )
    assert result == [
        datetime(2024, 1, 10),
        datetime(2025, 1, 10),
        datetime(2026, 1, 10),
        datetime(2027, 1, 10),
        datetime(2028, 1, 10),
        datetime(2029, 1, 10),
    ]


def test_generate_monthly_date_range():
    expected_dates = [
        datetime(2023, 1, 14),
        datetime(2023, 2, 14),
        datetime(2023, 3, 14),
        datetime(2023, 4, 14),
        datetime(2023, 5, 14),
        datetime(2023, 6, 14),
        datetime(2023, 7, 14),
        datetime(2023, 8, 14),
        datetime(2023, 9, 14),
        datetime(2023, 10, 14),
        datetime(2023, 11, 14),
        datetime(2023, 12, 14),
        datetime(2024, 1, 14),
        datetime(2024, 2, 14),
        datetime(2024, 3, 14),
    ]
    assert (
        generate_monthly_date_range(
            start_date=datetime(2023, 1, 14), end_date=datetime(2024, 3, 14)
        )
        == expected_dates
    )


def test_generate_monthly_date_range_bom():
    expected_dates = [
        datetime(2023, 1, 1),
        datetime(2023, 2, 1),
        datetime(2023, 3, 1),
        datetime(2023, 4, 1),
        datetime(2023, 5, 1),
        datetime(2023, 6, 1),
        datetime(2023, 7, 1),
        datetime(2023, 8, 1),
        datetime(2023, 9, 1),
        datetime(2023, 10, 1),
        datetime(2023, 11, 1),
        datetime(2023, 12, 1),
        datetime(2024, 1, 1),
        datetime(2024, 2, 1),
        datetime(2024, 3, 1),
    ]
    assert (
        generate_monthly_date_range(
            start_date=datetime(2023, 1, 1), end_date=datetime(2024, 3, 1)
        )
        == expected_dates
    )


def test_generate_monthly_date_range_eom():
    expected_dates = [
        datetime(2023, 1, 31),
        datetime(2023, 2, 28),
        datetime(2023, 3, 31),
        datetime(2023, 4, 30),
        datetime(2023, 5, 31),
        datetime(2023, 6, 30),
        datetime(2023, 7, 31),
        datetime(2023, 8, 31),
        datetime(2023, 9, 30),
        datetime(2023, 10, 31),
        datetime(2023, 11, 30),
        datetime(2023, 12, 31),
        datetime(2024, 1, 31),
        datetime(2024, 2, 29),
        datetime(2024, 3, 31),
    ]
    assert (
        generate_monthly_date_range(
            start_date=datetime(2023, 1, 31), end_date=datetime(2024, 3, 31)
        )
        == expected_dates
    )


def test_string_to_datetime():
    date = string_to_datetime("2022-01-18")
    assert isinstance(date, datetime)
    assert date == datetime(2022, 1, 18)


def test_datetime_to_string():
    date = datetime_to_string(datetime(2022, 1, 18))
    assert isinstance(date, str)
    assert date == "2022-01-18"


@pytest.mark.parametrize(
    "input_date, months_to_add, expected_output",
    [
        (datetime(2022, 1, 31), 1, datetime(2022, 2, 28)),
        (datetime(2020, 1, 31), 1, datetime(2020, 2, 29)),
        (datetime(2020, 1, 31), 15, datetime(2021, 4, 30)),
        (datetime(2020, 12, 31), 15, datetime(2022, 3, 31)),
    ],
)
def test_last_date_in_next_month(input_date, months_to_add, expected_output):
    assert last_date_in_next_month(input_date, months_to_add) == expected_output


@pytest.mark.parametrize(
    "input_date, months_to_add, expected_output",
    [
        (datetime(2022, 1, 14), 1, datetime(2022, 2, 14)),
        (datetime(2020, 1, 14), 1, datetime(2020, 2, 14)),
        (datetime(2020, 1, 14), 15, datetime(2021, 4, 14)),
        (datetime(2020, 12, 14), 15, datetime(2022, 3, 14)),
        (datetime(2022, 1, 31), 1, datetime(2022, 2, 28)),
        (datetime(2020, 1, 31), 1, datetime(2020, 2, 29)),
        (datetime(2020, 1, 31), 15, datetime(2021, 4, 30)),
        (datetime(2020, 1, 11), 39, datetime(2023, 4, 11)),
    ],
)
def test_same_or_last_date_in_next_month(input_date, months_to_add, expected_output):
    assert same_or_last_date_in_next_month(input_date, months_to_add) == expected_output
