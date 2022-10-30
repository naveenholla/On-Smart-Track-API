from ontrack.lookup.models import Setting as AdminSetting
from ontrack.utils.config import Configurations as config
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger


class SettingLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def can_execute_task(self, date_key, pause_hours_key):
        last_execute_date_str = AdminSetting.backend.get_setting(date_key)

        if last_execute_date_str is None:
            return True

        pause_hours = 0
        if pause_hours_key is not None:
            pause_hours = AdminSetting.backend.get_setting(pause_hours_key)
            if pause_hours is None:
                pause_hours = config.get_default_value_by_key(pause_hours)

        last_execute_date = dt.str_to_datetime(last_execute_date_str)
        nextRunDay = dt.get_future_date(date=last_execute_date, hours=pause_hours)
        return dt.compare_current_date_time(nextRunDay, "lte")

    def save_task_execution_time(self, date_key):
        AdminSetting.backend.save_setting(
            date_key,
            dt.datetime_to_str(dt.current_date_time()),
        )
