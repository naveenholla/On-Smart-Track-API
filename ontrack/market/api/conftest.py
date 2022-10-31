import pytest

from ontrack.market.api.logic.lookup import InitializeData
from ontrack.market.api.tests.factories import ExchangeFactory
from ontrack.market.models.lookup import Exchange


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        obj = InitializeData("nse")
        obj.load_fixtures_data()


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


@pytest.fixture(autouse=True)
def exchange_fixture(db) -> Exchange:
    return ExchangeFactory()
