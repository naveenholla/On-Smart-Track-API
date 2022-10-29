import pytest

from ontrack.utils.numbers import NumberHelper as nh


@pytest.mark.unittest
def test_ceil():
    value = nh.ceil(27.0 / 4)
    assert value == 7

    value = nh.ceil(27.5 / 4)
    assert value == 7

    value = nh.ceil(26 / 4)
    assert value == 7

    value = nh.ceil(25 / 4)
    assert value == 7

    value = nh.ceil(24 / 4)
    assert value == 6


def test_roundOff():
    value = nh.roundOff(3.367824)
    assert value == 3.37

    value = nh.roundOff(4.56782)
    assert value == 4.57

    value = nh.roundOff(4.56722, 4)
    assert value == 4.5672

    value = nh.roundOff(4.56725, 4)
    assert value == 4.5672

    value = nh.roundOff(4.56726, 4)
    assert value == 4.5673


@pytest.mark.unittest
def test_str_to_float():
    value = nh.str_to_float(None)
    assert value == 0

    value = nh.str_to_float(26.0)
    assert value == 26.0
    assert isinstance(value, float)

    value = nh.str_to_float("2222126.55   ")
    assert value == 2222126.55
    assert isinstance(value, float)

    value = nh.str_to_float("-")
    assert value == 0.00

    value = nh.str_to_float("NIL")
    assert value == 0.00

    value = nh.str_to_float("   ")
    assert value == 0.00

    value = nh.str_to_float("")
    assert value == 0.00

    value = nh.str_to_float("5487")
    assert value == 5487
    assert isinstance(value, float)


@pytest.mark.unittest
def test_round_to_market_Price():
    value = nh.round_to_market_Price(23.23)
    assert value == 23.25

    value = nh.round_to_market_Price(23.20)
    assert value == 23.20

    value = nh.round_to_market_Price(23.99)
    assert value == 24

    value = nh.round_to_market_Price(4.5673)
    assert value == 4.6

    value = nh.round_to_market_Price(4.5373)
    assert value == 4.55


@pytest.mark.unittest
def test_get_nearest_strike_price():
    value = nh.get_nearest_strike_price(40990.85, 100)
    assert value == 41000

    value = nh.get_nearest_strike_price(40090.85, 100)
    assert value == 40100

    value = nh.get_nearest_strike_price(40020.85, 100)
    assert value == 40000

    value = nh.get_nearest_strike_price(40030.85, 50)
    assert value == 40050

    value = nh.get_nearest_strike_price(33.65, 2.5)
    assert value == 32.5


@pytest.mark.unittest
def test_get_upper_lower_limit():
    value = nh.get_upper_lower_limit(18010, 50, 20)
    assert value == (17050, 18950)

    value = nh.get_upper_lower_limit(18030, 100, 10)
    assert value == (17100, 18900)
