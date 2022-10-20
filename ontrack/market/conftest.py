import pytest

from ontrack.market.data.common import CommonDataPull
from ontrack.market.data.equity import PullEquityData
from ontrack.market.data.index import PullIndexData
from ontrack.market.data.tests.factories import (
    EquityFactory,
    ExchangeFactory,
    IndexFactory,
)
from ontrack.market.models.lookup import Equity, Exchange, Index
from ontrack.utils.config import Configurations


@pytest.fixture(autouse=True)
def exchange_fixture(db) -> Exchange:
    return ExchangeFactory()


@pytest.fixture(autouse=True)
def equity_fixture(db) -> Equity:
    return EquityFactory()


@pytest.fixture(autouse=True)
def index_fixture(db) -> Index:
    return IndexFactory()


@pytest.fixture
def equity_data_fixture():
    def _method(exchange_symbol):
        exchange_queryset = Exchange.datapull_manager.all()
        equity_queryset = Equity.datapull_manager.get_queryset()

        assert exchange_queryset.count() == 1

        urls = Configurations.get_urls_config()
        listed_equities = urls["listed_equities"]
        fo_marketlot = urls["fo_marketlot"]

        pull_equity_obj = PullEquityData(
            exchange_queryset,
            equity_queryset,
            listed_equities,
            fo_marketlot,
            exchange_symbol,
        )
        return pull_equity_obj.pull_and_parse_equity_data()

    return _method


@pytest.fixture
def index_data_fixture():
    def _method(exchange_symbol):
        exchange_queryset = Exchange.datapull_manager.all()
        index_queryset = Index.datapull_manager.all()
        assert exchange_queryset.count() == 1

        urls = Configurations.get_urls_config()
        indices_percentage = urls["indices_percentage"]
        fo_marketlot = urls["fo_marketlot"]

        pull_index_obj = PullIndexData(
            exchange_queryset,
            index_queryset,
            indices_percentage,
            fo_marketlot,
            exchange_symbol,
        )
        return pull_index_obj.pull_and_parse_indice_data()

    return _method


@pytest.fixture(autouse=True)
def equity_index_data_fixture(
    exchange_fixture, equity_data_fixture, index_data_fixture
):
    indices = index_data_fixture(exchange_fixture.symbol)
    equities = equity_data_fixture(exchange_fixture.symbol)
    datapull = CommonDataPull()

    datapull.create_or_update(indices, Index, Index.datapull_manager)
    datapull.create_or_update(equities, Equity, Equity.datapull_manager)
