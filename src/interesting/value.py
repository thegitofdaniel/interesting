from datetime import datetime

from pydantic import BaseModel, validator


class Value(BaseModel):
    value: float | int
    price_date: str | datetime

    @validator("price_date")
    def check_date_format(cls, v):  # noqa: N805
        if isinstance(v, str):
            try:
                datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                raise ValueError("Date string must be in 'YYYY-MM-DD' format")
        return v

    @property
    def formatted_date(self):
        if isinstance(self.price_date, datetime):
            return self.price_date.strftime("%Y-%m-%d")
        return self.price_date

    def __str__(self):
        return f"Value(value={self.value:,.2f}, price_date='{self.formatted_date}')"

    def __repr__(self):
        return self.__str__()

    def _is_same_price_date(self, other):
        if self.price_date != other.price_date:
            raise ValueError("Cannot compare values from different price_dates.")

    def __add__(self, other):
        if isinstance(other, int | float):
            return Value(value=self.value + other, price_date=self.price_date)
        if isinstance(other, Value):
            self._is_same_price_date(other)
            return Value(value=self.value + other.value, price_date=self.price_date)

    def __sub__(self, other):
        if isinstance(other, int | float):
            return Value(value=self.value - other, price_date=self.price_date)
        if isinstance(other, Value):
            self._is_same_price_date(other)
            return Value(value=self.value - other, price_date=self.price_date)

    def __rsub__(self, other):
        if isinstance(other, int | float):
            return Value(value=other - self.value, price_date=self.price_date)
        if isinstance(other, Value):
            self._is_same_price_date(other)
            return Value(value=other.value - self.value, price_date=self.price_date)

    def __eq__(self, other):
        assert isinstance(other, Value)
        return self.value == other.value and self.price_date == other.price_date
