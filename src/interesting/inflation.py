from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from interesting.interest import InterestRate
from interesting.time import (
    datetime_to_string,
    det_freq_of_date_range,
    same_or_last_date_in_next_month,
)

from .utils import date_format_from_freq, figsize_medium


class InflationCuve:
    def __init__(self):
        self.data = pd.DataFrame()

    def __str__(self):
        index = self.data.index
        return f"Price-Level-Inflation: ({datetime_to_string(min(index))},{datetime_to_string(max(index))}) with {len(index)} rows."

    def __repr__(self):
        return self.__str__()

    # ------------------------------
    # load data
    def from_json(self, rows):
        data = pd.DataFrame(rows)
        data["date"] = pd.to_datetime(data["date"])
        data = data.set_index("date")
        self.data = data
        return self

    def from_constant(
        self,
        start_date: datetime | str,
        end_date: datetime | str,
        inflation: InterestRate,
    ):
        # initialize vars
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        assert start_date < end_date

        dates = []
        current_date = end_date

        # index
        if inflation.freq == "Y":
            step = 12
        elif inflation.freq == "S":
            step = 6
        elif inflation.freq == "M":
            step = 1
        else:
            raise ValueError("Invalid freq")
        n_months = 0
        while current_date > start_date:
            dates.append(current_date)
            n_months -= step
            current_date = same_or_last_date_in_next_month(
                reference_date=end_date, months_forward=n_months
            )
        dates = sorted(dates)

        # interest calendar
        df = pd.DataFrame(index=dates)
        df["inflation"] = inflation.value

        df = df.rename_axis("date")
        self.data = df
        self.freq = det_freq_of_date_range(self.data.index)
        self.inflation_to_price_level()
        return self

    # ------------------------------
    # price management

    def inflation_to_price_level(self):
        # _except_irregular_index(data)
        level_col = "price_level"
        delta_col = "inflation"
        assert delta_col in self.data.columns
        data = self.data
        data[level_col] = (1 + data[delta_col]).cumprod()
        data[level_col] /= data[level_col].iloc[0]
        self.data = data
        return self

    def price_level_to_inflation(self):
        # _except_irregular_index(data)
        level_col = "price_level"
        delta_col = "inflation"
        assert "price_level" in self.data.columns
        # loses one row
        data = self.data
        data[delta_col] = data[level_col].pct_change()
        data = data.dropna()
        self.data = data
        return self

    def yield_to_inflation(self):
        # _except_irregular_index(data)
        assert "real_yield" in self.data.columns
        assert "nominal_yield" in self.data.columns
        data = self.data
        data["inflation"] = (1 + data["nominal_yield"]) / (1 + data["real_yield"]) - 1
        self.data = data
        return self

    # ------------------------------
    # operations
    def get_deflator_curve(self, price_date):
        data = self.data
        level_col = "price_level"
        series = data[level_col] / data[level_col][price_date]
        data = pd.DataFrame(series).rename(columns={level_col: "deflator"})
        return data

    # -----------------------------------------------------
    # Plots

    def _plot_and_annotate(self, label, ax, marker):
        xs = self.data.index
        ys = self.data[label]
        ax.plot(xs, ys, label=label, marker=marker, linestyle="-", markersize=10)
        rotation = 45 if len(xs) > 12 else 0
        for x, y in zip(xs, ys):
            ax.annotate(
                f"{y:,.3f}",
                (x, y),
                textcoords="offset points",
                xytext=(0, 20 if y >= 0 else -20),
                ha="center",
                rotation=rotation,
            )

    def _format_x_axis(self, ax, dates):
        rotation = 45 if len(dates) > 12 else 0
        freq = det_freq_of_date_range(self.data.index)
        date_format = date_format_from_freq(freq)
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

    def plot_inflation(self) -> plt.Figure:
        fig, ax1 = plt.subplots(figsize=figsize_medium)

        dates = self.data.index

        level_labels = ["price_level"]
        for label in level_labels:
            self._plot_and_annotate(label=label, ax=ax1, marker="o")
        self._format_y_axis(ax1)

        yield_labels = ["real_yield", "nominal_yield", "inflation"]
        yield_labels = [label for label in yield_labels if label in self.data.columns]
        if len(yield_labels) > 0:
            ax2 = ax1.twinx()
            for label in yield_labels:
                self._plot_and_annotate(label=label, ax=ax2, marker="X")
            self._format_y_axis(ax2)

        self._format_x_axis(ax1, dates)

        # shared elements
        ax1.grid(True, which="major", linestyle="--", linewidth=0.5)
        ax1.set_title(level_labels + yield_labels)
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        fig.set_facecolor("lightgrey")
        plt.tight_layout()
        plt.close(fig)

        return fig
