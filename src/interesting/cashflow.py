# general
from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy_financial as npf
import pandas as pd

from .interest import CompoundInterestRate
from .time import (
    calculate_delta_freq,
    calculate_delta_years,
    datetime_to_string,
    det_freq_of_date_range,
    generate_freq_date_range,
    same_or_last_date_in_next_month,
    string_to_datetime,
)
from .utils import calc_brazilian_tax_rate, date_format_from_freq
from .value import Value


class Cashflow:
    def __init__(self):
        self.data = pd.DataFrame()
        # XXX
        # self.freq
        # self.start_date
        # self.end_date
        # self.capital

    def __str__(self):
        index = self.data.index
        start_date = datetime_to_string(min(index))
        end_date = datetime_to_string(max(index))
        n_obs = len(index)
        return f"Cashflow: from {start_date} to {end_date} with {n_obs} rows."

    def __repr__(self):
        return self.__str__()

    # ------------------------------
    # load data

    @classmethod
    def from_pandas(cls, df):
        instance = cls()
        data = df.copy()
        if "date" in data.columns:
            data["date"] = pd.to_datetime(data["date"])
            data = data.set_index("date")
            data = data.rename_axis("date")
        else:
            data.index = pd.DatetimeIndex(data.index)
        if data.index.name != "date":
            raise ValueError("Index must be named 'date'.")
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError(
                f"Index must be pd.DatetimeIndex. Instead, it is {type(data.index)}."
            )

        instance.data = data
        instance.freq = det_freq_of_date_range(data.index)
        return instance

    @classmethod
    def from_json(cls, rows):
        return cls.from_pandas(pd.DataFrame(rows))

    @classmethod
    def det_dates(cls, start_date, end_date, freq, n_periods):
        """Determine date range from:
        - start_date + end_date + freq
        - endData + n_periods + freq of pmts
        - start_date + n_periods + freq
        """
        months_in_freq = {
            "Y": 12,
            "S": 6,
            "Q": 3,
            "M": 1,
            "D": 1 / 30,
        }
        if start_date is not None and end_date is not None:
            pass
        elif n_periods is not None:
            n_periods_in_months = n_periods * months_in_freq[freq]
            if end_date is not None:
                start_date = same_or_last_date_in_next_month(
                    end_date, -n_periods_in_months
                )
            elif start_date is not None:
                end_date = same_or_last_date_in_next_month(
                    start_date, n_periods_in_months
                )
            else:
                start_date = pd.to_datetime(datetime.now().date())
                end_date = same_or_last_date_in_next_month(
                    start_date, n_periods_in_months
                )
        else:
            raise ValueError()
        dates = generate_freq_date_range(start_date, end_date, freq)
        return dates

    @classmethod
    def gen_amount_pmts(
        cls, pmt_amount, n_periods, gradient_yield=0.0, gradient_amount=0.0
    ):
        if gradient_yield != 0.0:
            pmts = [
                pmt_amount * (1 + gradient_yield) ** period
                for period in range(n_periods)
            ]
        else:
            pmts = [
                (pmt_amount + gradient_amount * period) for period in range(n_periods)
            ]
        return pmts

    @classmethod
    def from_regular_pmt(
        cls,
        pmt_amount,
        freq,
        start_date=None,
        end_date=None,
        n_periods=None,
        initial_capital_pmt=0,
        final_capital_pmt=0,
        gradient_yield=0.0,
        gradient_amount=0.0,
    ):
        if isinstance(start_date, str):
            start_date = string_to_datetime(start_date)

        if isinstance(end_date, str):
            end_date = string_to_datetime(end_date)

        dates = cls.det_dates(
            start_date=start_date,
            end_date=end_date,
            n_periods=n_periods,
            freq=freq,
        )
        start_date = dates[0]
        end_date = dates[-1]

        pmts = cls.gen_amount_pmts(
            pmt_amount=pmt_amount,
            n_periods=len(dates) - 1,
            gradient_yield=gradient_yield,
            gradient_amount=gradient_amount,
        )
        df = pd.DataFrame(index=dates).rename_axis("date")
        df["interest_paid"] = [0] + pmts
        df["principal"] = 0.0
        df.at[start_date, "principal"] = initial_capital_pmt
        df.at[end_date, "principal"] = final_capital_pmt
        df["brutto"] = df["principal"] + df["interest_paid"]
        return cls.from_pandas(df=df)

    @classmethod
    def gen_interest_pmts(
        cls,
        interest_rate,
        n_periods,
        initial_capital_pmt,
        inflation_rate=0,
        gradient_yield=0.0,
    ):
        pmts = [
            (1 + interest_rate * ((1 + gradient_yield) ** period))
            * (1 + inflation_rate)
            - 1
            for period in range(0, n_periods)
        ]
        pmts = [-initial_capital_pmt * p for p in pmts]
        return pmts

    @classmethod
    def from_regular_interest(
        cls,
        interest,
        freq,
        inflation=CompoundInterestRate(value=0.0, freq="Y"),
        start_date=None,
        end_date=None,
        n_periods=None,
        initial_capital_pmt=0,
        final_capital_pmt=0,
        gradient_yield=0.0,
    ):
        if isinstance(start_date, str):
            start_date = string_to_datetime(start_date)

        if isinstance(end_date, str):
            end_date = string_to_datetime(end_date)

        dates = cls.det_dates(
            start_date=start_date,
            end_date=end_date,
            n_periods=n_periods,
            freq=freq,
        )
        start_date = dates[0]
        end_date = dates[-1]
        if freq != "F":
            interest = interest.convert_to_equivalent(new_freq=freq)
            inflation = inflation.convert_to_equivalent(new_freq=freq)
            pmts = cls.gen_interest_pmts(
                interest_rate=interest.value,
                inflation_rate=inflation.value,
                n_periods=len(dates) - 1,
                initial_capital_pmt=initial_capital_pmt,
                gradient_yield=gradient_yield,
            )
        else:
            delta_time = calculate_delta_freq(
                start_date=start_date, end_date=end_date, freq=interest.freq
            )
            pmts = [
                interest.future_value(
                    present_value=-initial_capital_pmt, delta_time=delta_time
                )
                * (1 + inflation.value) ** (delta_time)
                + initial_capital_pmt
            ]
        df = pd.DataFrame(index=dates).rename_axis("date")
        df["interest_paid"] = [0] + pmts
        df["principal"] = 0.0
        df.at[start_date, "principal"] = initial_capital_pmt
        df.at[end_date, "principal"] = final_capital_pmt
        df["brutto"] = df["principal"] + df["interest_paid"]
        return cls.from_pandas(df=df)

    @classmethod
    def from_equal_pmts(
        cls,
        interest,
        initial_capital_pmt,
        freq,
        start_date=None,
        end_date=None,
        n_periods=None,
    ):
        dates = cls.det_dates(
            start_date=start_date,
            end_date=end_date,
            n_periods=n_periods,
            freq=freq,
        )

        def calc_equal_pmt(initial_capital_pmt, interest_rate, n_periods):
            pmt_factor = (
                (1 + interest_rate) ** n_periods
                * interest_rate
                / ((1 + interest_rate) ** n_periods - 1)
            )
            installment_pmt = -initial_capital_pmt * pmt_factor
            return installment_pmt

        pmt = calc_equal_pmt(
            initial_capital_pmt=initial_capital_pmt,
            interest_rate=interest.value,
            n_periods=len(dates) - 1,
        )

        instance = cls.from_regular_pmt(
            pmt_amount=pmt,
            freq=freq,
            start_date=start_date,
            end_date=end_date,
            n_periods=n_periods,
            initial_capital_pmt=initial_capital_pmt,
        )

        instance.data = instance.data[["brutto"]]

        return instance

    # ------------------------------
    # query
    def get_dates(self):
        return list(self.data.index)

    def get_cols(self):
        return list(self.data.columns)

    def get_point(self, point):
        return self.data.loc[point]

    # ------------------------------
    # aggregation

    def agg_to_freq(self, freq: str):
        assert freq in {
            "ME",
            "YE",
            "QE",
            "BME",
            "BYE",
            "BQE",
            "W",
        }, "Pandas only allows limited frequencies."
        data = self.data.copy()
        data = data.resample(freq).sum()
        self.data = data
        if freq in ["ME", "BME"]:
            self.freq = "M"
        elif freq in ["YE", "BYE"]:
            self.freq = "Y"
        elif freq in ["QE", "BQE"]:
            self.freq = "Q"
        elif freq in ["W"]:
            self.freq = "W"
        return self

    # ------------------------------
    # validation
    def _index_is_regular(self):
        dates = self.data.index
        freq = det_freq_of_date_range(dates)
        if freq not in {"M", "S", "Y", "F"}:
            return False
        return True

    def _except_irregular_index(self):
        if not self._index_is_regular():
            raise ValueError("Irregular index.")

    # ------------------------------
    # tax
    @staticmethod
    def _set_principal_and_interest(df: pd.DataFrame):
        data = df.copy()
        initial_value = data["brutto"].values[0]
        data["principal"] = 0
        data.loc[data.index.min(), "principal"] = initial_value
        data.loc[data.index.max(), "principal"] = -initial_value
        data["interest_paid"] = data["brutto"] - data["principal"]
        return data

    @staticmethod
    def _calculat_tax(df: pd.DataFrame):
        data = df.copy()
        data["delta_days"] = (data.index - data.index.min()).days
        data["taxRate"] = data["delta_days"].apply(calc_brazilian_tax_rate)
        data["tax"] = data["interest_paid"] * data["taxRate"]
        return data

    def tax(self):
        data = self.data.copy()
        if ("principal" not in data.columns) and ("interest_paid" not in data.columns):
            data = self._set_principal_and_interest(data)
        data = self._calculat_tax(data)
        data["netto"] = data["brutto"] - data["tax"]
        self.data = data
        return self

    # ------------------------------
    # valuation
    def discount_from_constant_rate(self, interest, target):
        # XXX assumption: regular freq

        self._except_irregular_index()
        data = self.data.copy()
        data[f"{target}_discount_yield"] = interest.value
        data[f"{target}_discount_yield"] = (
            data[f"{target}_discount_yield"].shift(1).fillna(0)
        )
        data[f"{target}_discount_factor"] = (
            1 / (1 + data[f"{target}_discount_yield"]).cumprod()
        )
        data[f"{target}_present_value"] = (
            data[target] * data[f"{target}_discount_factor"]
        )
        self.data = data
        return self

    def discount_from_yield_curve(self, discount_curve, target):
        self._except_irregular_index()
        data = self.data.copy()
        data[f"{target}_discount_yield"] = discount_curve.values
        data[f"{target}_discount_factor"] = (
            1 / (1 + data[f"{target}_discount_yield"]).cumprod()
        )
        data[f"{target}_present_value"] = (
            data[target] * data[f"{target}_discount_factor"]
        )
        self.data = data
        return self

    def npv(self, target, interest=None):
        if interest is not None:
            self.discount_from_constant_rate(interest=interest, target=target)
        col = f"{target}_present_value"
        if col not in self.data.columns:
            raise ValueError(f"Error: '{col} not in columns=={self.data.columns}.")
        npv = Value(value=self.data[col].sum(), price_date=self.data.index.min())
        return npv

    def irr(self, target):
        self._except_irregular_index()
        # XXX get rid of npf
        return CompoundInterestRate(
            value=npf.irr(self.data[target].values),
            freq=self.freq,
        ).convert_to_equivalent(new_freq="Y")

    #     def mirr(self, tartget_cols, reinvestment_rate):
    #         # XXX implement
    #         pass

    def print_npv_and_irr(self, target):
        print(f"col: {target}")
        irr = self.irr(target)
        print(f"irr: {irr}")
        npv = self.npv(target)
        print(f"npv: {npv}")

    # ------------------------------
    # inflation
    def deflate_from_constant(self, constant: float, target: str, new_price_date=None):
        data = self.data.copy()
        if new_price_date is None:
            new_price_date = self.data.index.min()
        if isinstance(new_price_date, str):
            new_price_date = datetime.strptime(new_price_date, "%Y-%m-%d")
        data["delta_years"] = data.index.map(
            lambda date: calculate_delta_years(start_date=new_price_date, end_date=date)
        )
        data["deflator"] = (1 + constant) ** data["delta_years"]
        data["deflator"] /= data["deflator"][new_price_date]
        data[f"{target}_deflated"] = data[target] / data["deflator"]
        self.data = data
        return self

    def deflate_from_deflator_curve(self, target, deflator_curve):
        data = self.data.copy()
        data["deflator"] = deflator_curve.values
        data[f"{target}_deflated"] = data[target] / data["deflator"]
        self.data = data
        return self

    """
    def deflate_from_InflationCuve(self, target, InflationCuve):
        data = self.data.copy()
        deflator_curve = "XXX"
        return self.deflate_from_deflator_curve(target=target, deflator_curve=deflator_curve)

    def deflate_from_price_level_curve(self, target, price_level_curve):
        data = self.data.copy()
        deflator_curve = "XXX"
        return self.deflate_from_deflator_curve(target=target, deflator_curve=deflator_curve)
    """

    # -----------------------------------------------------
    # Operations

    def add_cashflow(self, other_cashflow):
        df1 = self.data
        df2 = other_cashflow.data
        if df1.shape[0] == 0:
            sum_df = df2
        elif df2.shape[0] == 0:
            sum_df = df1
        else:
            # XXX which cols to sum?
            cols = {"brutto", "interest_paid", "principal"}
            cols = cols.intersection(set(df1.columns), set(df2.columns))
            cols = list(cols) + ["date"]
            df1 = df1.reset_index().sort_index(axis=1)[cols]
            df2 = df2.reset_index().sort_index(axis=1)[cols]
            assert all(df1.columns == df2.columns)
            sum_df = pd.concat([df1, df2], axis=0, ignore_index=True)
            sum_df = sum_df.groupby("date").sum()
            sum_df = sum_df.sort_index()
        sum_cf = Cashflow().from_pandas(sum_df)
        self.cashflow = sum_cf
        # XXX properties
        return sum_cf

    def __add__(self, other_cashflow):
        return self.add_cashflow(other_cashflow)

    # -----------------------------------------------------
    # Plots

    def _plot_and_annotate(self, label, ax, marker):
        dates = self.data.index()
        y = self.data[label]
        ax.plot(dates, y, label=label, marker=marker, linestyle="-", markersize=10)
        rotation = 45 if len(dates) > 12 else 0
        for date, y in zip(dates, y):
            ax.annotate(
                f"{y:,.3f}",
                (date, y),
                textcoords="offset points",
                xytext=(0, 20 if y >= 0 else -20),
                ha="center",
                rotation=rotation,
            )

    def _format_x_axis(self, ax, dates):
        rotation = 45 if len(dates) > 12 else 0
        date_format = date_format_from_freq(self.freq)
        ax.set_xticks(dates)
        plt.xticks(rotation=rotation)
        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        ax.set_xlabel("time")
        return ax

    def _format_y_axis(self, ax):
        ax.axhline(0, color="black")
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        return ax

    def plot_line(self, labels: list[str] | None = None) -> plt.Figure:
        self._exceptEmpty()
        labels = self.labels if labels is None else labels
        fig, ax = plt.subplots(1, figsize=(18, 12))
        dates = self.data.index
        for label in labels:
            self._plot_and_annotate(label=label, ax=ax, marker="o")
        self._format_x_axis(ax=ax, dates=dates)
        self._format_y_axis(ax=ax)
        ax.grid(True, which="major", linestyle="--", linewidth=0.5)
        fig.set_facecolor("lightgrey")
        plt.tight_layout()
        plt.close(fig)

        return fig

    def plot_arrow(self, targets=list[str]):
        fig, ax = plt.subplots(1, figsize=(18, 12))

        for target in targets:
            dates = self.data.index
            amounts = self.data[target]

            max_amount = max(abs(amount) for amount in amounts)
            for date, amount in zip(dates, amounts):
                if abs(amount) > max_amount / 5:
                    head_length = max_amount / 10
                else:
                    head_length = amount / 2

                arrow_color = "green" if amount >= 0 else "red"
                ax.arrow(
                    date,
                    0,
                    0,
                    amount,
                    color=arrow_color,
                    width=2,
                    head_width=5,
                    head_length=head_length,
                    length_includes_head=True,
                    label=target,
                )

                rotation = 45 if len(dates) > 12 else 0

                ax.annotate(
                    f"{amount:,.0f}",
                    (date, amount),
                    textcoords="offset points",
                    xytext=(0, 20 if amount >= 0 else -20),
                    ha="center",
                    rotation=rotation,
                )

        # Set x-axis locator and formatter
        self._format_x_axis(ax, dates)
        self._format_y_axis(ax)
        ax.set_title(f"Cashflow - {targets}")
        fig.set_facecolor("lightgrey")
        plt.tight_layout()

        # Clear the current figure to prevent duplicate images
        plt.close(fig)

        return fig
