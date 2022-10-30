import pytest
from freezegun import freeze_time

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.lookup.models import Setting
from ontrack.utils.base.enum import AdminSettingKey
from ontrack.utils.datetime import DateTimeHelper as dt


class TestSettingData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.setting_qs = Setting.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def setting_data_fixture(self, setting_fixture):
        self.setting_fixture = setting_fixture
        self.setting_logic = SettingLogic()

    @pytest.mark.unittest
    def test_can_execute_task(self):
        date_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_DATE
        pause_hour_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS
        date = dt.get_date_time(2022, 10, 20, 9, 15, 0)

        with freeze_time(date):
            assert self.setting_logic.can_execute_task(
                "Non-Existing-Key", "pause-hours-key"
            )

            self.setting_logic.save_task_execution_time(date_key)
            assert not self.setting_logic.can_execute_task(date_key, pause_hour_key)

        date = dt.get_future_date(date, hours=201)
        with freeze_time(date):
            assert self.setting_logic.can_execute_task(date_key, pause_hour_key)
