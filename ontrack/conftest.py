import pytest
from _pytest.mark import Mark

from ontrack.users.models.user import User
from ontrack.users.tests.factories import UserFactory

empty_mark = Mark("", [], {})


def by_slow_marker(item):
    return item.get_closest_marker("slow", default=empty_mark)


def pytest_addoption(parser):
    parser.addoption("--slow-last", action="store_true", default=True)


def pytest_collection_modifyitems(items, config):
    if config.getoption("--slow-last"):
        items.sort(key=by_slow_marker, reverse=False)


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user(db) -> User:
    return UserFactory()
