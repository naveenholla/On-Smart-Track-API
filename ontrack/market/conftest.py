import pytest

from ontrack.market.data.tests.factories import EquityFactory, ExchangeFactory
from ontrack.market.models.lookup import Equity, Exchange


@pytest.fixture(autouse=True)
def exchange_fixture(db) -> Exchange:
    return ExchangeFactory()


@pytest.fixture(autouse=True)
def equity_fixture(db) -> Equity:
    return EquityFactory()
