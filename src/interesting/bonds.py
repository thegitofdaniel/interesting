from datetime import datetime

import pandas as pd

from .cashflow import Cashflow
from .interest import InterestRate
from .utils import bonds_info


class Bond(Cashflow):
    def __init__(
        self, name: str, species: str, issuer: str, is_nominal: bool, cashflow: Cashflow
    ):
        self.data = cashflow.data
        self.name = name
        self.species = species
        self.issuer = issuer
        self.is_nominal = is_nominal
        self.is_fgc = bonds_info[species]["is_fgc"]
        self.is_taxable = bonds_info[species]["is_taxable"]


class RealBond(Bond):
    def __init__(
        self,
        name,
        species,
        issuer,
        freq,
        index_name,
        start_date: datetime,
        end_date: datetime,
        interest: InterestRate | pd.DataFrame,
        initial_capital_pmt: float | int,
        inflation=None,
    ):
        cashflow = Cashflow().from_regular_interest(
            start_date=start_date,
            end_date=end_date,
            interest=interest,
            inflation=inflation,
            freq=freq,
            initial_capital_pmt=initial_capital_pmt,
            final_capital_pmt=-initial_capital_pmt,
        )
        super().__init__(
            name=name,
            species=species,
            issuer=issuer,
            is_nominal=False,
            cashflow=cashflow,
        )
        self.index_name = index_name


class NominalBond(Bond):
    def __init__(
        self,
        name,
        species,
        issuer,
        freq,
        start_date: datetime,
        end_date: datetime,
        interest: InterestRate | pd.DataFrame,
        initial_capital_pmt: float | int,
    ):
        cashflow = Cashflow().from_regular_interest(
            interest=interest,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            n_periods=None,
            initial_capital_pmt=initial_capital_pmt,
            final_capital_pmt=-initial_capital_pmt,
        )
        super().__init__(
            name=name,
            species=species,
            issuer=issuer,
            is_nominal=True,
            cashflow=cashflow,
        )


class NTNB(RealBond):
    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        interest: InterestRate | pd.DataFrame,
        initial_capital_pmt: float | int,
        inflation: InterestRate | None = None,
    ):
        super().__init__(
            name="ntnb",
            species="ntnb",
            issuer="tesouro nacional",
            index_name="ipca",
            freq="S",
            start_date=start_date,
            end_date=end_date,
            inflation=inflation.convert_to_equivalent(new_freq="S"),
            interest=interest.convert_to_equivalent(new_freq="S"),
            initial_capital_pmt=initial_capital_pmt,
        )


class LTN(NominalBond):
    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        interest: InterestRate | pd.DataFrame,
        initial_capital_pmt: float | int,
    ):
        super().__init__(
            name="ltn",
            species="ltn",
            issuer="tesouro nacional",
            freq="F",
            start_date=start_date,
            end_date=end_date,
            interest=interest.convert_to_equivalent(new_freq="Y"),
            initial_capital_pmt=initial_capital_pmt,
        )
