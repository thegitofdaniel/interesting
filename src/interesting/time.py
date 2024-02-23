from datetime import datetime, timedelta

# ----------------------------------------------------------------------
# format


def string_to_datetime(date_string: str, format_str="%Y-%m-%d") -> datetime:
    return datetime.strptime(date_string, format_str)


def datetime_to_string(dt_obj: datetime, format_str="%Y-%m-%d") -> str:
    return dt_obj.strftime(format_str)


# ----------------------------------------------------------------------
# date checks


def is_valid_date(date_string, format_str: str = "%Y-%m-%d") -> bool:
    try:
        if isinstance(date_string, str):
            string_to_datetime(date_string, format_str)
        else:
            datetime_to_string(date_string, format_str)
        return True
    except ValueError:
        return False


def is_leap_year(year: float | int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def is_same_date(start_date: datetime, end_date: datetime) -> bool:
    return start_date.month == end_date.month and start_date.day == end_date.day


def is_same_day(start_date: datetime, end_date: datetime) -> bool:
    return start_date.day == end_date.day


def is_last_day_of_month(check_date) -> bool:
    next_month_first_day = check_date.replace(month=(check_date.month % 12) + 1, day=1)
    last_day_of_month = next_month_first_day - timedelta(days=1)
    return check_date.day == last_day_of_month.day


def validatedate_range(dates: list[str], freq="Y"):
    assert freq in ["Y", "S", "M"]
    date_range_freq = det_freq_of_date_range(dates)
    assert (
        date_range_freq == freq
    ), f"Date range freq doesn't match the expected freq. {date_range_freq} != {freq}"


# ----------------------------------------------------------------------
# calculate delta freqs


def calculate_delta_years(start_date: datetime, end_date: datetime) -> float | int:
    if is_same_date(start_date, end_date):
        delta_years = end_date.year - start_date.year
        return delta_years

    elif is_last_day_of_month(start_date) and is_last_day_of_month(end_date):
        delta_years = (end_date.year - start_date.year) + (
            end_date.month - start_date.month
        ) / 12
        return delta_years

    else:
        delta_years = (
            (end_date.year - start_date.year)
            + (end_date.month - start_date.month) / 12
            + (end_date.day - start_date.day) / 365
        )

        leap_years = sum(
            1
            for year in range(start_date.year, end_date.year + 1)
            if is_leap_year(year)
        )
        delta_years -= leap_years / 365

    return delta_years


def calculate_delta_months(start_date: datetime, end_date: datetime) -> int | float:
    if is_same_date(start_date, end_date):
        delta_years = (end_date.year - start_date.year) * 12
        return delta_years

    elif is_same_day(start_date, end_date):
        delta_years = (end_date.year - start_date.year) * 12 + (
            end_date.month - start_date.month
        )
        return delta_years

    elif is_last_day_of_month(start_date) and is_last_day_of_month(end_date):
        delta_years = (end_date.year - start_date.year) * 12 + (
            end_date.month - start_date.month
        )
        return delta_years

    else:
        delta_years = (
            (end_date.year - start_date.year) * 12
            + (end_date.month - start_date.month)
            + (end_date.day - start_date.day) / 30
        )

        leap_years = sum(
            1
            for year in range(start_date.year, end_date.year + 1)
            if is_leap_year(year)
        )
        delta_years -= leap_years / 365.0

    return delta_years


def calculate_delta_freq(
    start_date: datetime, end_date: datetime, freq: str
) -> int | float:
    assert freq in ["Y", "S", "M"], f"freq=={freq}, but must be 'Y', 'S', or 'M'."

    if freq == "Y":
        time_delta = calculate_delta_years(start_date, end_date)
    elif freq == "S":
        time_delta = calculate_delta_months(start_date, end_date) / 6
    else:
        time_delta = calculate_delta_months(start_date, end_date)

    return time_delta


# ----------------------------------------------------------------------
# calculate dates


def last_day_of_month(date: datetime) -> int:
    last_day_of_each_month_non_leap = {
        1: 31,
        2: 28,
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }
    last_day = last_day_of_each_month_non_leap[date.month]
    if date.month == 2 and is_leap_year(date.year):
        last_day += 1
    return last_day


def last_date_in_next_month(reference_date, months_forward: int = 1) -> str:
    delta_years = months_forward // 12
    delta_months = months_forward % 12

    next_year = reference_date.year + delta_years
    next_month = reference_date.month + delta_months

    if next_month > 12:
        next_month = next_month % 12
        next_year += 1

    next_day = last_day_of_month(datetime(next_year, next_month, 1))
    next_date = datetime(next_year, next_month, next_day)

    return next_date


def same_or_last_date_in_next_month(reference_date, months_forward: int):
    delta_years = months_forward // 12
    delta_months = months_forward % 12

    next_year = reference_date.year + delta_years
    next_month = reference_date.month + delta_months

    if next_month > 12:
        next_month = next_month % 12
        next_year += 1

    next_day = min(
        last_day_of_month(datetime(next_year, next_month, 1)), reference_date.day
    )

    next_date = datetime(next_year, next_month, next_day)

    return next_date


# ----------------------------------------------------------------------
# generate date ranges


def generate_freq_date_range(start_date: datetime, end_date: datetime, freq: str):
    if freq == "F":
        date_range = [start_date, end_date]
    elif freq == "Y":
        date_range = generate_yearly_date_range(start_date, end_date)
    elif freq == "S":
        date_range = generate_semiannual_date_range(start_date, end_date)
    elif freq == "M":
        date_range = generate_monthly_date_range(start_date, end_date)
    else:
        raise ValueError(f"freq=={freq}, but must be 'F', 'Y', 'S', 'M'.")
    return date_range


def generate_yearly_date_range(start_date, end_date):
    assert start_date <= end_date, "Start date must be before end date."

    num_years = int(calculate_delta_years(start_date, end_date) // 1 + 1)

    date_range = []
    for n in range(num_years):
        nth_year = start_date.year + n
        nth_date = start_date.replace(year=nth_year)
        date_range.append(nth_date)
    return date_range


def generate_monthly_date_range(start_date, end_date):
    assert start_date <= end_date, "Start date must be before end date."

    date_range = []
    next_date = start_date

    months_forward = 0
    if is_last_day_of_month(start_date):
        while next_date <= end_date:
            date_range.append(next_date)
            months_forward += 1
            next_date = last_date_in_next_month(start_date, months_forward)

    else:
        while next_date <= end_date:
            date_range.append(next_date)
            months_forward += 1
            next_date = same_or_last_date_in_next_month(start_date, months_forward)

    return date_range


def generate_semiannual_date_range(start_date, end_date):
    assert start_date <= end_date, "Start date must be before end date."

    date_range = []
    next_date = start_date

    months_forward = 0
    if is_last_day_of_month(start_date):
        while next_date <= end_date:
            date_range.append(next_date)
            months_forward += 6
            next_date = last_date_in_next_month(start_date, months_forward)

    else:
        while next_date <= end_date:
            date_range.append(next_date)
            months_forward += 6
            next_date = same_or_last_date_in_next_month(start_date, months_forward)

    return date_range


# ----------------------------------------------------------------------
# det freq


def det_freq_of_date_range(date_range):
    start_date = min(date_range)
    end_date = max(date_range)
    candidate_freqs = ["Y", "S", "M"]
    for freq in candidate_freqs:
        candidatedate_range = generate_freq_date_range(start_date, end_date, freq)
        if len(candidatedate_range) != len(date_range):
            continue
        elif all(candidatedate_range == date_range):
            return freq
    return "X"
