from ontrack.lookup.models import Setting as AdminSetting
from ontrack.utils.base.enum import SettingKeyType
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.numbers import NumberHelper as nh


class SettingLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def get_by_key(self, key, default_value_key=None, default_value=None):
        value = AdminSetting.backend.get_setting(key)

        if value is None and default_value_key is not None:
            value = AdminSetting.backend.get_setting(default_value_key)

        if value is None:
            return default_value

        return value

    def can_execute_task(self, date_key, pause_hours_key, default_value_key=None):
        last_execute_date_str = self.get_by_key(
            date_key, default_value_key=default_value_key
        )

        if last_execute_date_str is None:
            return True, dt.current_date_time()

        pause_hours = "0"
        if pause_hours_key is not None:
            pause_hours = self.get_by_key(pause_hours_key)
            pause_hours = nh.str_to_float(pause_hours)

        last_execute_date = dt.str_to_datetime(last_execute_date_str)
        nextRunDay = dt.get_future_date(date=last_execute_date, hours=pause_hours)
        return dt.compare_current_date_time(nextRunDay, "gte"), nextRunDay

    def save_task_execution_time(
        self, date_key, date=None, key_type=SettingKeyType.EXECUTION_TIME
    ):
        if date is None:
            date = dt.current_date_time()
        date_str = dt.datetime_to_str(date)
        self.save_setting(date_key, date_str, key_type)

    def save_setting(self, key, value, key_type=SettingKeyType.CONFIGURATION):
        AdminSetting.backend.save_setting(key, value, key_type)
