import pytest
from _pytest.mark import Mark

from ontrack.market.data.initialize import InitializeData
from ontrack.market.data.tests.factories import ExchangeFactory
from ontrack.market.models.lookup import Exchange


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        InitializeData().load_fixtures_data()


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
