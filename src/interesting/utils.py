from collections import OrderedDict

# ----------------------------------------------------------------------
# Constants

bonds_info = {
    "poupanca": {"is_fgc": True, "is_taxable": True},
    "cdb": {"is_fgc": True, "is_taxable": True},
    "lc": {"is_fgc": True, "is_taxable": True},
    "lh": {"is_fgc": True, "is_taxable": True},
    "lci": {"is_fgc": True, "is_taxable": False},
    "lca": {"is_fgc": True, "is_taxable": False},
    "debinc": {"is_fgc": False, "is_taxable": False},
    "deb": {"is_fgc": False, "is_taxable": True},
    "lf": {"is_fgc": False, "is_taxable": True},
    "fundo": {"is_fgc": False, "is_taxable": True},
    "cri": {"is_fgc": False, "is_taxable": False},
    "cra": {"is_fgc": False, "is_taxable": False},
    "lig": {"is_fgc": False, "is_taxable": True},
    "vgbl": {"is_fgc": False, "is_taxable": True},
    "pgbl": {"is_fgc": False, "is_taxable": True},
    "ntnb": {"is_fgc": False, "is_taxable": True},
}


# ipca
# https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html?=&t=downloads

brazilian_tax_rate_after_n_days = {0: 0.225, 181: 0.20, 361: 0.175, 721: 0.15}

# focus: up until 2027 (Jan 2024)
brazil_focus_inflation_ipca = {
    "2024": 0.0381,
    "2025": 0.0350,
    "2026": 0.0350,
    "2027": 0.0350,
}

figsize_medium = (12, 6)


def calc_brazilian_tax_rate(days):
    if not isinstance(days, int) or days < 0:
        raise ValueError("days should be a non-negative integer.")
    tax_rate_brackets = OrderedDict([(0, 0.225), (181, 0.2), (361, 0.175), (721, 0.15)])
    for upper_bound, rate in tax_rate_brackets.items():
        if days < upper_bound:
            return rate
    return rate


# ----------------------------------------------------------------------
# maths


def is_close(a, b, epsilon=1e-10) -> bool:
    return abs(a - b) < epsilon


def is_whole_number(number) -> bool:
    return number % 1 == 0


# ----------------------------------------------------------------------
# formatting


def thousand_separator(x, _):
    return f"{x:,.0f}"


def date_format_from_freq(freq: str) -> str:
    if freq == "Y":
        date_format = "%Y"
    elif freq == "S" or freq == "M":
        date_format = "%Y-%m"
    else:
        date_format = "%Y-%m-%d"
    return date_format


# ----------------------------------------------------------------------
# finance


def future_value(present_value: float, interest_rate: float, freqs: float) -> float:
    future_value = present_value * (1 + interest_rate) ** freqs
    return future_value


def present_value(future_value: float, interest_rate: float, freqs: float) -> float:
    present_value = future_value / (1 + interest_rate) ** freqs
    return present_value


# ----------------------------------------------------------------------
# querying


def find_last_less_than_x(numbers, x):
    for number in numbers:
        if number < x:
            last_less_than_x = number
    return last_less_than_x


# ----------------------------------------------------------------------
# sorting


def sort_dict_by_key(data: dict) -> OrderedDict:
    sorted_data = sorted(data.items(), key=lambda x: x[0])
    ordered_dict = OrderedDict(sorted_data)
    return ordered_dict


def sort_dict_by_value(data: dict) -> OrderedDict:
    sorted_data = sorted(data.items(), key=lambda x: x[1])
    ordered_dict = OrderedDict(sorted_data)
    return ordered_dict


# ----------------------------------------------------------------------
# filtering


def remove_entries_with_zero(odict: OrderedDict) -> OrderedDict:
    keys_to_remove = [key for key, value in odict.items() if value == 0]
    for key in keys_to_remove:
        del odict[key]
    return odict


def remove_boundary_entries_with_zero(odict) -> OrderedDict:
    leading_zeros = []
    for key, value in odict.items():
        if value == 0:
            leading_zeros.append(key)
        else:
            break
    trailing_zeros = []
    for key, value in odict.items().__reversed__():
        if value == 0:
            trailing_zeros.append(key)
        else:
            break
    keys_to_remove = leading_zeros + trailing_zeros
    for key in keys_to_remove:
        del odict[key]
    return odict
