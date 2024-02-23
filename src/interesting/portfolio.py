from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

from .cashflow import Cashflow
from .utils import thousand_separator

figsize_medium = (18, 12)


class Portfolio:
    def __init__(self):
        self.bonds = []
        self.total_cashflow = Cashflow()

    def __str__(self):
        return f"Portfolio: {len(self.bonds)} Cashflows."

    def __repr__(self):
        return self.__str__()

    def __add__(self, other):
        if not isinstance(other, Portfolio):
            raise TypeError(
                "Unsupported operand type(s) for +: 'Portfolio' and '{}'".format(
                    type(other).__name__
                )
            )
        new_portfolio = Portfolio()
        new_portfolio.bonds = self.bonds + other.bonds
        new_portfolio.total_cashflow = self.total_cashflow + other.total_cashflow
        return new_portfolio

    # ------------------------------
    # add data
    def add_bond(self, bond):
        if isinstance(bond, list):
            self.bonds.extend(bond)
            self.total_cashflow += bond
        else:
            self.bonds.append(bond)
        self.total_cashflow += bond
        return self

    # ------------------------------
    # query data

    def filter_portfolio(self, properties: dict):
        # properties = {"is_fgc": True, "is_taxable": True}
        new_portfolio = Portfolio()
        for bond in self.bonds:
            keep = True
            for key, value in properties.items():
                if bond.__getattribute__(key) != value:
                    keep = False
                    break
            if keep:
                new_portfolio.add_bond(bond)
        return new_portfolio

    def get_target_sum_by_property(
        self,
        target: str = "brutto",
        property: str = "issuer",
        future_only: bool = True,
        past_only: bool = False,
    ) -> dict[str, float]:
        bonds_by_property = {}
        for bond in self.bonds:
            if property == "issuer":
                value = bond.issuer
            elif property == "species":
                value = bond.species
            elif property == "index_name":
                value = bond.index_name
            elif property == "is_nominal":
                value = bond.is_nominal
            elif property == "is_fgc":
                value = bond.is_fgc
            elif property == "is_taxable":
                value = bond.is_taxable
            else:
                raise ValueError("Invalid property.")

            if value in bonds_by_property:
                bonds_by_property[value].append(bond)
            else:
                bonds_by_property[value] = [bond]

        bonds_by_property_agg = {}
        for property in bonds_by_property.keys():
            cf = Cashflow()
            for bond in bonds_by_property[property]:
                cf += bond
            bonds_by_property_agg[property] = cf

        data = {}
        for property in bonds_by_property_agg.keys():
            cf = bonds_by_property_agg[property]
            if future_only:
                df_subset = cf.data[target][cf.data.index >= datetime.today()]
            elif past_only:
                df_subset = cf.data[target][cf.data.index < datetime.today()]
            else:
                df_subset = cf.data[target]
            data[property] = sum(df_subset)
        return data

    def group_by_year(self) -> dict[str, float]:
        list_of_dfs = [bond.data.reset_index() for bond in self.bonds]
        df = pd.concat(list_of_dfs, axis=0, ignore_index=True)
        df["year"] = df["date"].apply(lambda x: x.year)
        df = df.drop(columns=["date"]).groupby(["year"]).sum()
        return df

    # ------------------------------
    # XXX discount and valuation

    # ------------------------------
    # plot
    @staticmethod
    def plot_pie(data: dict, title=""):
        sorted_data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
        fig, ax = plt.subplots(figsize=figsize_medium)
        plt.pie(sorted_data.values(), labels=sorted_data.keys(), autopct="%1.1f%%")
        plt.title(title)
        plt.show()

    @staticmethod
    def plot_bar(data: dict, title="", fgc_line=False):
        # XXX add an argument acc_line to plot the accumulated value -> this is useful in making the plot of when an issuer pays the money back
        data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))

        fig, ax = plt.subplots(figsize=figsize_medium)
        bars = ax.bar(data.keys(), data.values())

        for bar, cashflow in zip(bars, data.values()):
            height = bar.get_height()
            y_offset = 3 if height >= 0 else -24
            ax.annotate(
                f"{cashflow:,.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, y_offset),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                rotation=60,
            )

        ax.yaxis.set_major_formatter(FuncFormatter(thousand_separator))

        plt.xlabel("XXX")
        plt.ylabel("XXX")
        plt.title(title)

        if fgc_line:
            plt.axhline(
                y=250000, color="r", linestyle="--", label="FGC Protection By Issuer"
            )

        plt.show()

    def plot_target_by_property(self, target, property, graph="pie"):
        if property == "year":
            df = self.group_by_year()
            data = df[target].to_dict()
        else:
            data = self.get_target_sum_by_property(
                property=property, target=target, future_only=True
            )
        if graph == "pie":
            return self.plot_pie(data=data, title=f"{target} by {property}")
        else:
            return self.plot_bar(data=data, title=f"{target} by year")

    def plot_fgc_risk(self, target):
        fgc_portfolio = self.filter_portfolio(properties={"is_fgc": True})
        data = fgc_portfolio.get_target_sum_by_property(
            property="issuer", target=target, future_only=True
        )
        return self.plot_bar(data=data, title=f"{target} by year", fgc_line=True)

    def plot_issuer_by_year(self, target, issuer):
        fgc_portfolio = self.filter_portfolio(properties={"issuer": issuer})
        return fgc_portfolio.plot_target_by_property(
            target=target, property="year", graph="bar"
        )
