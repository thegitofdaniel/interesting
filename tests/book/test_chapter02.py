import pandas as pd

from src.interesting.cashflow import Cashflow
from src.interesting.interest import CompoundInterestRate


def test_c02_e01():
    freq = "M"
    n_periods = 100
    cf = Cashflow.from_regular_pmt(
        pmt_amount=250,
        n_periods=n_periods,
        freq=freq,
    )
    interest = CompoundInterestRate(value=0.03, freq=freq)
    present_value = cf.npv(target="brutto", interest=interest)
    assert round(present_value.value, 2) == 7899.73
    # XXX future value should be a Value ??
    future_value = interest.future_value(
        present_value=present_value.value, delta_time=n_periods
    )
    assert round(future_value, 2) == 151821.93


def test_c02_e02():
    freq = "M"
    n_periods = 150
    cf = Cashflow.from_regular_pmt(
        pmt_amount=350,
        n_periods=n_periods,
        freq=freq,
    )
    interest = CompoundInterestRate(value=0.025, freq=freq)
    present_value = cf.npv(target="brutto", interest=interest)
    # XXX add parameter to anticipate present value?
    ancitcipated_present_value = interest.future_value(
        present_value=present_value.value, delta_time=1
    )
    assert round(ancitcipated_present_value, 2) == 13996.60
    future_value = interest.future_value(
        present_value=ancitcipated_present_value, delta_time=n_periods
    )
    assert round(future_value, 2) == 568332.14


def test_c02_e03():
    n_periods = 24
    df = pd.DataFrame(
        index=pd.date_range(start="31/1/2020", periods=n_periods + 1, freq="ME")
    ).rename_axis("date")
    df["brutto"] = [-22500] + [1250] * 12 + [1650] * 12
    cf = Cashflow.from_pandas(df=df)
    r = cf.irr("brutto")
    assert round(r.convert_to_equivalent(new_freq="M").value, 4) == 0.0355


def test_c02_e04():
    cf = Cashflow.from_regular_pmt(
        pmt_amount=150, n_periods=100, freq="M", gradient_amount=150
    )
    present_value = cf.npv(
        target="brutto", interest=CompoundInterestRate(value=0.012, freq="M")
    )
    assert round(present_value.value, 2) == 355190.06


def test_c02_e05():
    freq = "M"
    n_periods = 35
    cf = Cashflow.from_regular_pmt(
        pmt_amount=1500,
        gradient_amount=150,
        n_periods=n_periods,
        freq=freq,
    )
    interest = CompoundInterestRate(value=0.015, freq=freq)

    present_value = cf.npv(target="brutto", interest=interest)
    ancicipated_present_value = interest.future_value(
        present_value=present_value.value, delta_time=1
    )
    assert round(ancicipated_present_value, 2) == 105068.95
    future_value = interest.future_value(
        present_value=ancicipated_present_value, delta_time=n_periods
    )
    assert round(future_value, 2) == 176923.65


def test_c02_e06():
    freq = "M"
    n_periods = 120
    cf = Cashflow.from_regular_pmt(
        pmt_amount=4500,
        gradient_yield=0.025,
        n_periods=n_periods,
        freq=freq,
    )
    interest = CompoundInterestRate(value=0.009, freq=freq)
    present_value = cf.npv(target="brutto", interest=interest)
    ancicipated_present_value = interest.future_value(
        present_value=present_value.value, delta_time=1
    )
    assert round(ancicipated_present_value, 2) == 1590814.36
    future_value = interest.future_value(
        present_value=ancicipated_present_value, delta_time=n_periods
    )
    assert round(future_value, 2) == 4661862.41


# def test_c02_e07():
#     pass

# XXX 08, 09,


def test_c02_e18():
    dates = pd.date_range(start="2020-01-31", periods=100, freq="ME")
    df = pd.DataFrame(index=dates).rename_axis("date")
    brutto = [6000 - (100 * n) for n in range(50)] + [
        1100 + (100 * n) for n in range(50)
    ]
    df["brutto"] = brutto

    cf = Cashflow.from_pandas(df)

    interest = CompoundInterestRate(value=0.01, freq="M")
    present_value = cf.npv(interest=interest, target="brutto").value
    present_value_anticipated = interest.present_value(present_value, 1)
    assert round(present_value_anticipated, 2) == 226922.99

    future_value = interest.future_value(present_value_anticipated, 100)
    assert round(future_value, 2) == 613784.43


def test_c02_e19():
    cf = Cashflow.from_regular_pmt(
        pmt_amount=650, n_periods=30, freq="M", gradient_yield=0.10
    )
    present_value = cf.npv(
        target="brutto", interest=CompoundInterestRate(value=0.02, freq="M")
    )
    assert round(present_value.value, 2) == 70145.62
