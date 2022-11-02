from ontrack.lookup.models import Setting as AdminSetting
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.numbers import NumberHelper as nh


class SettingLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def can_execute_task(self, date_key, pause_hours_key):
        last_execute_date_str = AdminSetting.backend.get_setting(date_key)

        if last_execute_date_str is None:
            return True, dt.current_date_time()

        pause_hours = "0"
        if pause_hours_key is not None:
            pause_hours = AdminSetting.backend.get_setting(pause_hours_key)
            pause_hours = nh.str_to_float(pause_hours)

        last_execute_date = dt.str_to_datetime(last_execute_date_str)
        nextRunDay = dt.get_future_date(date=last_execute_date, hours=pause_hours)
        return dt.compare_current_date_time(nextRunDay, "gte"), nextRunDay

    def save_task_execution_time(self, date_key, date=None):
        if date is None:
            date = dt.current_date_time()
        date_str = dt.datetime_to_str(date)
        AdminSetting.backend.save_setting(date_key, date_str)
