import pytest
from _pytest.mark import Mark

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


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        CommonDataPull().load_lookup_data()


# # conftest.py
# def pytest_collection_modifyitems(items):
#     """Modifies test items in place to ensure test classes run in a given order."""
#     CLASS_ORDER = ["TestPullEquityData", "TestPullIndexData", "TestPullEquityIndexData"]
#     class_mapping = {item: item.cls.__name__ for item in items}

#     sorted_items = items.copy()
#     # Iteratively move tests of each class to the end of the test queue
#     for class_ in CLASS_ORDER:
#         sorted_items = [it for it in sorted_items if class_mapping[it] != class_] + [
#             it for it in sorted_items if class_mapping[it] == class_
#         ]
#     items[:] = sorted_items

empty_mark = Mark("", [], {})


def by_slow_marker(item):
    return item.get_closest_marker("slow", default=empty_mark)


def pytest_addoption(parser):
    parser.addoption("--slow-last", action="store_true", default=True)


def pytest_collection_modifyitems(items, config):
    if config.getoption("--slow-last"):
        items.sort(key=by_slow_marker, reverse=False)


@pytest.fixture(autouse=True)
def exchange_fixture(db) -> Exchange:
    return ExchangeFactory()


@pytest.fixture(autouse=True)
def equity_fixture(db) -> Equity:
    return EquityFactory()


@pytest.fixture(autouse=True)
def index_fixture(db) -> Index:
    return IndexFactory()


@pytest.fixture(autouse=True)
def equity_data_fixture(
    equity_fixture: EquityFactory, exchange_fixture: ExchangeFactory
):
    def _method(exchange_symbol):
        exchange_queryset = Exchange.datapull_manager.all()
        equity_queryset = Equity.datapull_manager.all()
        assert exchange_queryset.count() > 0

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


@pytest.fixture(autouse=True)
def index_data_fixture(index_fixture: IndexFactory, exchange_fixture: ExchangeFactory):
    def _method(exchange_symbol):
        exchange_queryset = Exchange.datapull_manager.all()
        index_queryset = Index.datapull_manager.all()
        assert exchange_queryset.count() > 0

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
    exchange_fixture,
    index_fixture,
    equity_fixture,
    equity_data_fixture,
    index_data_fixture,
):
    indices = index_data_fixture(exchange_fixture.symbol)
    equities = equity_data_fixture(exchange_fixture.symbol)
    datapull = CommonDataPull()

    datapull.create_or_update(indices, Index, Index.datapull_manager)
    datapull.create_or_update(equities, Equity, Equity.datapull_manager)

    assert Index.datapull_manager.all().count() == len(indices)
    assert Equity.datapull_manager.all().count() == len(equities)
