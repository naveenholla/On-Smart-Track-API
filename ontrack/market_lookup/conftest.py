import pytest

from ontrack.market_lookup.data.tests.factories import EquityFactory, ExchangeFactory
from ontrack.market_lookup.models import Equity, Exchange


@pytest.fixture(autouse=True)
def exchange_fixture(db) -> Exchange:
    return ExchangeFactory()


@pytest.fixture(autouse=True)
def equity_fixture(db) -> Equity:
    return EquityFactory()
