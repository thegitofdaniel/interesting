import pytest

from src.interesting.interest import (
    CompoundInterestRate,
    ContinuousInterestRate,
    InterestRateCurve,
    SimpleInterestRate,
)


@pytest.mark.parametrize(
    "interest_class, expected_value",
    [
        (CompoundInterestRate, 1200),
        (SimpleInterestRate, 1200),
        (ContinuousInterestRate, 1221.40),
    ],
)
def test_c01_e01(interest_class, expected_value):
    delta_years = 1
    present_value = 1000
    interest_rate_value = 0.20
    freq = "Y"
    r = interest_class(value=interest_rate_value, freq=freq)
    future_value = r.future_value(present_value, delta_years)
    assert round(future_value, 2) == expected_value


@pytest.mark.parametrize(
    "interest_class, expected_value",
    [
        (CompoundInterestRate, 0.1250),
        (SimpleInterestRate, 0.1250),
        (ContinuousInterestRate, 0.1178),
    ],
)
def test_c01_e02(interest_class, expected_value):
    delta_years = 1
    present_value = 100000
    future_value = 112500
    freq = "Y"
    r = interest_class.from_equation(
        present_value=present_value,
        future_value=future_value,
        delta_time=delta_years,
        freq=freq,
    )
    assert round(r.value, 4) == expected_value


@pytest.mark.parametrize(
    "interest_class, expected_value",
    [
        (CompoundInterestRate, 545454.55),
        (SimpleInterestRate, 545454.55),
        (ContinuousInterestRate, 542902.45),
    ],
)
def test_c01_e03(interest_class, expected_value):
    delta_years = 1
    future_value = 600000
    interest_rate_value = 0.10
    freq = "Y"
    r = interest_class(value=interest_rate_value, freq=freq)
    present_value = r.present_value(future_value, delta_years)
    assert round(present_value, 2) == expected_value


@pytest.mark.parametrize(
    "days, expected_value", [(12, 0.0070), (35, 0.0204), (87, 0.0508), (265, 0.1546)]
)
def test_c01_e04(days, expected_value):
    freq = "M"
    interest_rate_value = 0.0175
    r = SimpleInterestRate(value=interest_rate_value, freq=freq)
    r_daily = r.convert_to_equivalent(new_freq="D")
    assert round(days * r_daily.value, 4) == expected_value


@pytest.mark.parametrize(
    "days, expected_value", [(14, 0.0084), (63, 0.0376), (85, 0.0508), (516, 0.3082)]
)
def test_c01_e05(days, expected_value):
    freq = "Y"
    interest_rate_value = 0.215
    r = SimpleInterestRate(value=interest_rate_value, freq=freq)
    r_daily = r.convert_to_equivalent(new_freq="D")
    assert round(days * r_daily.value, 4) == expected_value


def test_c01_e06():
    freq = "Y"
    interest_rate_value = 0.12
    delta_years = 3.5
    present_value = 200000
    r = SimpleInterestRate(value=interest_rate_value, freq=freq)
    future_value = r.future_value(present_value, delta_years)
    expectedfuture_value = 284000
    assert future_value == expectedfuture_value
    interest_paid = future_value - present_value
    assert interest_paid == 84000


def test_c01_e07():
    future_value = 125000
    present_value = 95000
    freq = "Y"
    interest_rate_value = 0.2048
    r = SimpleInterestRate(value=interest_rate_value, freq=freq)
    delta_years = r.delta_time(future_value=future_value, present_value=present_value)
    assert round(delta_years * 360, 0) == 555


@pytest.mark.parametrize(
    "days, expected_value", [(21, 0.0105), (56, 0.0282), (235, 0.1237), (453, 0.2521)]
)
def test_c01_e08(days, expected_value):
    freq = "M"
    interest_rate_value = 0.015
    r = CompoundInterestRate(value=interest_rate_value, freq=freq)
    r_daily = r.convert_to_equivalent(new_freq="D")
    assert round((1 + r_daily.value) ** days - 1, 4) == expected_value


def test_c01_e09():
    interest_rate_value = 0.185
    freq = "Y"
    r = CompoundInterestRate(
        value=interest_rate_value, freq=freq
    ).convert_to_equivalent(new_freq="D")
    delta_days = 6 * 30 + 35
    present_value = 15000
    expectedfuture_value = 16600.36
    future_value = r.future_value(present_value, delta_days)
    assert round(future_value, 2) == expectedfuture_value


def test_c01_e10():
    future_value = 32250
    present_value = 25000
    freq = "Y"
    interest_rate_value = 0.215
    r = CompoundInterestRate(value=interest_rate_value, freq=freq)
    r_monthly = r.convert_to_equivalent(new_freq="M")
    delta_months = r_monthly.delta_time(
        future_value=future_value, present_value=present_value
    )
    assert round(delta_months, 2) == 15.69


def test_c01_e11():
    interest_rate_value = 0.05 / 2
    freq = "M"
    r = ContinuousInterestRate(value=interest_rate_value, freq=freq)
    delta_months = 5 * 12 + 3
    future_value = 250000
    present_value = r.present_value(future_value=future_value, delta_time=delta_months)
    expectedpresent_value = 51751.89
    assert round(present_value, 2) == expectedpresent_value


@pytest.mark.parametrize(
    "value, expected_value", [(0.0056, 0.00562), (0.0134, 0.01349), (0.2140, 0.23862)]
)
def test_c01_e12(value, expected_value):
    r = ContinuousInterestRate(value=value, freq="Y").convert_to_compound()
    assert round(r.value, 5) == expected_value


@pytest.mark.parametrize("days, expected_value", [(37, 0.0217), (387, 0.2269)])
def test_c01_e13(days, expected_value):
    interest_rate_value = 0.235
    freq = "Y"
    r = CompoundInterestRate(
        value=interest_rate_value, freq=freq
    ).convert_to_continuous()
    r_daily = r.convert_to_equivalent(new_freq="D")
    assert round(days * r_daily.value, 4) == expected_value


@pytest.mark.parametrize("days, expected_result", [(17, 0.0107), (371, 0.2610)])
def test_c01_e14(days, expected_result):
    interest_rate_value = 0.2250
    freq = "Y"
    r = ContinuousInterestRate(
        value=interest_rate_value, freq=freq
    ).convert_to_compound()
    r_daily = r.convert_to_equivalent(new_freq="D")
    assert round((1 + r_daily.value) ** days - 1, 4) == expected_result


@pytest.mark.parametrize(
    "regime, expected_value",
    [
        ("compound", 230361.74),
        ("simple", 229956.01),
        ("continuous", 230471.18),
    ],
)
def test_c01_e15(regime, expected_value):
    yields = [0.01, 0.015, 0.013, 0.014, 0.0164]
    initial_capital_pmt = 215234
    ic = InterestRateCurve(yields=yields, regime=regime).calc_future_value_from_yields(
        initial_capital_pmt
    )
    future_value = ic.get_future_value(len(yields) - 1)
    assert round(future_value, 2) == expected_value


@pytest.mark.parametrize(
    "regime, expected_value",
    [
        ("compound", 60135.16),
        ("simple", 59300.00),
        ("continuous", 60221.11),
    ],
)
def test_c01_e16(regime, expected_value):
    yields = [0.015] * 6 + [0.016] * 6
    initial_capital_pmt = 50000
    ic = InterestRateCurve(yields=yields, regime=regime).calc_future_value_from_yields(
        initial_capital_pmt
    )
    future_value = ic.get_future_value(len(yields) - 1)
    assert round(future_value, 2) == expected_value


def test_c01_e17():
    future_value = 2
    present_value = 1
    freq = "Y"
    interest_rate_value = 0.07
    r = CompoundInterestRate(value=interest_rate_value, freq=freq)
    delta_years = r.delta_time(future_value=future_value, present_value=present_value)
    assert round(delta_years, 0) == 10


def test_c01_e18():
    present_value = 10000
    r1 = CompoundInterestRate(value=0.025, freq="M").convert_to_equivalent(new_freq="Q")
    assert round(r1.value, 4) == 0.0769
    future_value1 = r1.future_value(present_value, 1)

    r2 = CompoundInterestRate(value=0.08, freq="Q")
    future_value2 = r2.future_value(present_value, 1)

    assert r1 < r2
    assert future_value1 < future_value2


def test_c01_e19():
    """This question was highly confusing, so it was skipped."""
    pass


def test_c01_e20():
    regime = "compound"
    expected_value = 0.0475
    yields = [0.045] * 3 + [0.050] * 3
    initial_capital_pmt = 1
    ic = InterestRateCurve(yields=yields, regime=regime).calc_future_value_from_yields(
        initial_capital_pmt
    )
    future_value = ic.get_future_value(len(yields) - 1)
    assert round(future_value ** (1 / 6) - 1, 5) == expected_value
