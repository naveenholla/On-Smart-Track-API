import pytest

from ontrack.market_lookup.logic.tests.factories import EquityFactory, ExchangeFactory
from ontrack.market_lookup.models import Equity, Exchange
from ontrack.users.models import User
from ontrack.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def exchange_fixture(db) -> Exchange:
    return ExchangeFactory()


@pytest.fixture
def equity_fixture(db) -> Equity:
    return EquityFactory()
