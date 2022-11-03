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
    def test_get_by_key(self):
        key = AdminSettingKey.DATAPULL_EOD_DATA_PAUSE_HOURS
        value = self.setting_logic.get_by_key(key)
        assert value is not None
        assert value == "24"

        value = self.setting_logic.get_by_key("NOT-EXITING-KEY")
        assert value is None

        value = self.setting_logic.get_by_key("NOT-EXITING-KEY", default_value="22")
        assert value == "22"

        key = "NOT-EXITING-KEY"
        default_value_key = "DEFAULT-NOT-EXISTING-KEY"
        expected_value = "testing-default-value"
        self.setting_logic.save_setting(default_value_key, expected_value)
        value = self.setting_logic.get_by_key(key, default_value_key=default_value_key)
        assert value is not None
        assert value == expected_value

    @pytest.mark.unittest
    def test_can_execute_task(self):
        date_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE
        pause_hour_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS
        date = dt.get_date_time(2022, 10, 20, 9, 15, 0)

        with freeze_time(date):
            assert self.setting_logic.can_execute_task(
                "Non-Existing-Key", "pause-hours-key"
            )[0]

            self.setting_logic.save_task_execution_time(date_key)
            assert not self.setting_logic.can_execute_task(date_key, pause_hour_key)[0]

        date = dt.get_future_date(date, hours=201)
        with freeze_time(date):
            assert self.setting_logic.can_execute_task(date_key, pause_hour_key)[0]

    @pytest.mark.unittest
    def test_can_execute_task_default_value_key(self):
        date_key = "Non-Existing-Key"
        pause_hour_key = AdminSettingKey.DATAPULL_EOD_DATA_PAUSE_HOURS
        default_value_key = AdminSettingKey.DEFAULT_START_DATE_EQUITY_DATA_PULL

        result = self.setting_logic.can_execute_task(
            date_key, pause_hour_key, default_value_key
        )
        assert result[0]
