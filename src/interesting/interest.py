import numpy as np
import pandas as pd
from numpy import diff, e, log
from pydantic import BaseModel, Field


class InterestRate(BaseModel):
    value: float | int
    freq: str = Field(..., strip_whitespace=True, to_upper=True, pattern=r"^[YSQMD]$")
    regime: str = Field(
        ...,
        strip_whitespace=True,
        to_upper=False,
        pattern=r"^(simple|compound|continuous)$",
    )

    def __str__(self):
        return f"InterestRate(value={self.value:.4f}, freq='{self.freq}', regime='{self.regime}')"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        # equivalent rates are not the same!
        assert isinstance(other, InterestRate)

        if self.freq != other.freq:
            other = other.convert_to_equivalent(new_freq=self.freq)
        if self.regime != other.regime:
            return self.convert_to_compound().value == self.convert_to_compound().value
        else:
            return self.value == other.value

    def __gt__(self, other):
        assert isinstance(other, InterestRate)
        if self.freq != other.freq:
            other = other.convert_to_equivalent(new_freq=self.freq)
        if self.regime != other.regime:
            return self.convert_to_compound().value > self.convert_to_compound().value
        else:
            return self.value > other.value

    def __lt__(self, other):
        assert isinstance(other, InterestRate)
        if self.freq != other.freq:
            other = other.convert_to_equivalent(new_freq=self.freq)
        if self.regime != other.regime:
            return self.convert_to_compound().value < self.convert_to_compound().value
        else:
            return self.value < other.value


class CompoundInterestRate(InterestRate):
    value: float | int
    freq: str = Field(..., strip_whitespace=True, to_upper=True, pattern=r"^[YSQMD]$")

    def __init__(self, value, freq):
        super().__init__(value=value, freq=freq, regime="compound")

    @classmethod
    def from_equation(
        cls,
        present_value: float | int,
        future_value: float | int,
        delta_time: float | int,
        freq: str,
    ):
        value = (future_value / present_value) ** (1 / delta_time) - 1
        return cls(value=value, freq=freq)

    # -------------------------------------------
    # time-travel

    def future_value(
        self,
        present_value: float | int,
        delta_time: float | int,
    ):
        future_value = present_value * (1 + self.value) ** delta_time
        return future_value

    def present_value(
        self,
        future_value: float | int,
        delta_time: float | int,
    ):
        present_value = future_value / (1 + self.value) ** delta_time
        return present_value

    def uniform_future_value(
        self,
        present_value: float | int,
        periods: int,
        anticipation: float | int = 0,
    ):
        factor = ((1 + self.value) ** periods - 1) / self.value
        future_value = present_value * factor
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value

    def ap_future_value(
        self,
        present_value: float | int,
        periods: int,
        gradient,
        anticipation: float | int = 0,
    ):
        factor = ((1 + self.value) ** periods - 1) / self.value
        if gradient > 0:
            future_value = (present_value / self.value) * (
                (1 + self.value) * factor - periods
            )
        else:
            future_value = (present_value / self.value) * (
                periods * (1 + self.value) ** periods - factor
            )
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value

    def gp_future_value(
        self,
        present_value: float | int,
        periods: int,
        gradient,
        anticipation: float | int = 0,
    ):
        future_value = present_value * (
            ((1 + self.value) ** periods - (1 + gradient) ** periods)
            / (self.value - gradient)
        )
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value

    def delta_time(self, future_value: float | int, present_value: float | int):
        return log(future_value / present_value) / log(1 + self.value)

    # -------------------------------------------
    # conversions

    def convert_to_equivalent(self, new_freq=str):
        freq_ratios = {"Y": 1, "S": 2, "Q": 4, "M": 12, "D": 360}
        assert new_freq in freq_ratios.keys(), f"new_freq=={new_freq}"
        ratio = freq_ratios[self.freq] / freq_ratios[new_freq]
        value = (1 + self.value) ** ratio - 1
        r_equivalent = CompoundInterestRate(value=value, freq=new_freq)
        return r_equivalent

    def convert_to_compound(self):
        return self

    def convert_to_simple(self):
        value = self.value
        r_simple = SimpleInterestRate(value=value, freq=self.freq)
        return r_simple

    def convert_to_continuous(self):
        value = log(1 + self.value)
        r_simple = ContinuousInterestRate(value=value, freq=self.freq)
        return r_simple


class SimpleInterestRate(InterestRate):
    value: float | int
    freq: str = Field(..., strip_whitespace=True, to_upper=True, pattern=r"^[YSQMD]$")

    def __init__(self, value, freq):
        super().__init__(value=value, freq=freq, regime="simple")

    @classmethod
    def from_equation(
        cls,
        present_value: float | int,
        future_value: float | int,
        delta_time: float | int,
        freq: str,
    ):
        value = (future_value / present_value - 1) / delta_time
        return cls(value=value, freq=freq)

    # -------------------------------------------
    # time-travel

    def future_value(self, present_value: float | int, delta_time: float | int):
        return present_value * (1 + self.value * delta_time)

    def present_value(self, future_value: float | int, delta_time: float | int):
        return future_value / (1 + self.value * delta_time)

    def delta_time(self, future_value: float | int, present_value: float | int):
        return (future_value / present_value - 1) / self.value

    # -------------------------------------------
    # conversions
    def convert_to_equivalent(self, new_freq=str):
        freq_ratios = {"Y": 1, "S": 6, "Q": 3, "M": 12, "D": 360}
        assert new_freq in freq_ratios.keys(), f"new_freq=={new_freq}"
        ratio = freq_ratios[self.freq] / freq_ratios[new_freq]
        value = ratio * self.value
        r_equivalent = SimpleInterestRate(value=value, freq=new_freq)
        return r_equivalent

    def convert_to_compound(self):
        value = self.value
        r_compound = CompoundInterestRate(value=value, freq=self.freq)
        return r_compound

    def convert_to_simple(self):
        return self

    def convert_to_continuous(self):
        value = log(1 + self.value)
        r_simple = ContinuousInterestRate(value=value, freq=self.freq)
        return r_simple

    def uniform_future_value(
        self,
        present_value: float | int,
        periods: int,
        anticipation: float | int = 0,
    ):
        factor = ((1 + self.value) ** periods - 1) / self.value
        future_value = present_value * factor
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value

    def ap_future_value(
        self,
        present_value: float | int,
        periods: int,
        gradient,
        anticipation: float | int = 0,
    ):
        factor = ((1 + self.value) ** periods - 1) / self.value
        if gradient > 0:
            future_value = (present_value / self.value) * (
                (1 + self.value) * factor - periods
            )
        else:
            future_value = (present_value / self.value) * (
                periods * (1 + self.value) ** periods - factor
            )
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value

    def gp_future_value(
        self,
        present_value: float | int,
        periods: int,
        gradient,
        anticipation: float | int = 0,
    ):
        future_value = present_value * (
            ((1 + self.value) ** periods - (1 + gradient) ** periods)
            / (self.value - gradient)
        )
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value


class ContinuousInterestRate(InterestRate):
    value: float | int
    freq: str = Field(..., strip_whitespace=True, to_upper=True, pattern=r"^[YSQMD]$")

    def __init__(self, value, freq):
        super().__init__(value=value, freq=freq, regime="continuous")

    @classmethod
    def from_equation(
        cls,
        present_value: float | int,
        future_value: float | int,
        delta_time: float | int,
        freq: str,
    ):
        value = log(future_value / present_value) / delta_time
        return cls(value=value, freq=freq)

    # -------------------------------------------
    # time-travel

    def future_value(self, present_value: float | int, delta_time: float | int):
        return present_value * e ** (self.value * delta_time)

    def present_value(self, future_value: float | int, delta_time: float | int):
        return future_value / e ** (self.value * delta_time)

    def delta_time(self, future_value: float | int, present_value: float | int):
        return log(future_value / present_value) / self.value

    # -------------------------------------------
    # conversions
    def convert_to_equivalent(self, new_freq=str):
        freq_ratios = {"Y": 1, "S": 6, "Q": 3, "M": 12, "D": 360}
        assert new_freq in freq_ratios.keys(), f"new_freq=={new_freq}"
        ratio = freq_ratios[self.freq] / freq_ratios[new_freq]
        value = ratio * self.value
        r_equivalent = ContinuousInterestRate(value=value, freq=new_freq)
        return r_equivalent

    def convert_to_compound(self):
        value = e**self.value - 1
        r_compound = CompoundInterestRate(value=value, freq=self.freq)
        return r_compound

    def convert_to_simple(self):
        value = log(1 + self.value)
        r_simple = SimpleInterestRate(value=value, freq=self.freq)
        return r_simple

    def convert_to_continuous(self):
        return self

    def gp_future_value(
        self,
        present_value: float | int,
        periods: int,
        gradient,
        anticipation: float | int = 0,
    ):
        future_value = present_value * (
            (e ** (self.value * periods) - e ** (gradient * periods))
            / (self.value - gradient)
        )
        if anticipation != 0:
            future_value = self.future_value(
                present_value=future_value, delta_time=anticipation
            )
        return future_value


class YearlyCompoundInterestRate(CompoundInterestRate):
    def __init__(self, value):
        super().__init__(value=value, freq="Y")

    @classmethod
    def from_equation(
        cls,
        present_value: float | int,
        future_value: float | int,
        delta_time: float | int,
    ):
        return super().from_equation(
            present_value=present_value,
            future_value=future_value,
            delta_time=delta_time,
            freq="Y",
        )


class YearlySimpleInterestRate(SimpleInterestRate):
    def __init__(self, value):
        super().__init__(value=value, freq="Y")

    @classmethod
    def from_equation(
        cls,
        present_value: float | int,
        future_value: float | int,
        delta_time: float | int,
    ):
        return super().from_equation(
            present_value=present_value,
            future_value=future_value,
            delta_time=delta_time,
            freq="Y",
        )


class YearlyContinuousInterestRate(ContinuousInterestRate):
    def __init__(self, value):
        super().__init__(value=value, freq="Y")

    @classmethod
    def from_equation(
        cls,
        present_value: float | int,
        future_value: float | int,
        delta_time: float | int,
    ):
        return super().from_equation(
            present_value=present_value,
            future_value=future_value,
            delta_time=delta_time,
            freq="Y",
        )


class InterestRateCurve:
    def __init__(self, yields, regime):
        assert isinstance(
            yields, list | np.ndarray
        ), "Yields must be a list or an array"
        assert all(
            isinstance(val, float) for val in yields
        ), "All elements in yields must be floats"
        assert isinstance(regime, str), "Regime must be a string"
        assert regime.lower() in [
            "compound",
            "simple",
            "continuous",
        ], "Regime must be 'compound', 'simple', or 'continuous'"
        self.data = pd.DataFrame(yields, columns=["yields"])
        self.regime = regime.lower()

    @classmethod
    def from_future_value(
        cls, future_value: list[float], regime: str
    ) -> "InterestRateCurve":
        assert len(future_value) > 0
        assert isinstance(future_value, list)
        assert isinstance(regime, str)
        assert regime in ["compound", "simple", "continuous"]
        future_value = np.array(future_value)
        df = pd.DataFrame({"future_value": future_value[1:]})
        firstpmt = future_value[0]
        if regime == "compound":
            df["yields"] = diff(future_value) / future_value[:-1]
        elif regime == "simple":
            df["yields"] = diff(future_value) / firstpmt
        else:
            df["yields"] = diff(log(future_value / firstpmt))
        return cls(yields=df["yields"].to_list(), regime=regime)

    def calc_acc_yield_factor(self):
        df = self.data
        assert "yields" in df.columns, "Yields column not found"
        if self.regime == "compound":
            df["acc_yield_factor"] = (1 + df["yields"]).cumprod()
        elif self.regime == "simple":
            df["acc_yield_factor"] = 1 + df["yields"].cumsum()
        else:
            df["acc_yield_factor"] = np.exp(df["yields"].cumsum())
        self.data = df
        return self

    def calc_future_value_from_yields(self, initial_capital_pmt) -> "InterestRateCurve":
        df = self.calc_acc_yield_factor().data
        df["future_value"] = df["acc_yield_factor"] * initial_capital_pmt
        self.data = df
        return self

    def get_future_value(self, period):
        return self.data.loc[period, "future_value"]
