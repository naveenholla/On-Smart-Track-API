import pytest

from ontrack.lookup.api.logic.lookup import InitializeData
from ontrack.lookup.api.tests.factories import SettingFactory
from ontrack.lookup.models import Setting


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        obj = InitializeData()
        obj.load_fixtures_all_data()


@pytest.fixture(autouse=True)
def setting_fixture(db) -> Setting:
    return SettingFactory()
