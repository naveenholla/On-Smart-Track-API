import pytest

from ontrack.utils.numbers import NumberHelper as nh


@pytest.mark.unittest
@pytest.mark.parametrize(
    "input,expected",
    [(6.75, 7), (6.875, 7), (6.5, 7), (6.25, 7), (6, 6)],
)
def test_ceil(input, expected):
    value = nh.ceil(input)
    assert value == expected


@pytest.mark.unittest
@pytest.mark.parametrize(
    "price,digits,expected",
    [
        (3.367824, None, 3.37),
        (4.56782, None, 4.57),
        (4.56742, 4, 4.5674),
        (4.56725, 4, 4.5672),
        (4.56726, 4, 4.5673),
    ],
)
def test_roundOff(price, digits, expected):
    if digits is not None:
        value = nh.roundOff(price, digits)
    else:
        value = nh.roundOff(price)
    assert value == expected


@pytest.mark.unittest
@pytest.mark.parametrize(
    "input,expected",
    [
        (None, 0),
        (26.0, 26.0),
        ("2222126.55   ", 2222126.55),
        ("-", 0.00),
        ("NIL", 0.00),
        ("    ", 0.00),
        ("", 0.00),
        ("5487", 5487.00),
    ],
)
def test_str_to_float(input, expected):
    value = nh.str_to_float(input)
    assert value == expected
    assert isinstance(value, float)


@pytest.mark.unittest
@pytest.mark.parametrize(
    "input,expected",
    [(23.23, 23.25), (23.20, 23.20), (23.99, 24), (4.5673, 4.6), (4.5373, 4.55)],
)
def test_round_to_market_Price(input, expected):
    value = nh.round_to_market_Price(input)
    assert value == expected


@pytest.mark.unittest
@pytest.mark.parametrize(
    "price, strikeDifference, expected",
    [
        (40990.85, 100, 41000),
        (40090.85, 100, 40100),
        (40020.85, 100, 40000),
        (40030.85, 50, 40050),
        (33.65, 2.5, 32.5),
    ],
)
def test_get_nearest_strike_price(price, strikeDifference, expected):
    value = nh.get_nearest_strike_price(price, strikeDifference)
    assert value == expected


@pytest.mark.unittest
@pytest.mark.parametrize(
    "price, strikeDifference, record_limit, expected",
    [(18010, 50, 20, (17050, 18950)), (18030, 100, 10, (17100, 18900))],
)
def test_get_upper_lower_limit(price, strikeDifference, record_limit, expected):
    value = nh.get_upper_lower_limit(price, strikeDifference, record_limit)
    assert value == expected
