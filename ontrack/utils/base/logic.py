from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger


class BaseLogic:
    def __init__(self):
        self.logger = ApplicationLogger()
        self.settings = SettingLogic()

    def can_execute_task(self, date_key, pause_hour_key, default_value_key=None):
        result = self.settings.can_execute_task(
            date_key, pause_hour_key, default_value_key
        )
        next_run_date = result[1]
        next_run_date_str = dt.datetime_to_display_str(result[1])

        if not result[0]:
            message = f"Task is paused for time being till {next_run_date_str}."
            self.logger.log_info(message)
            return False, message, next_run_date

        return True, None, next_run_date

    def message_creator(self, module_name, result):
        output = {}
        output["module"] = module_name
        if result is not None:
            if isinstance(result, str):
                output["message"] = result
            else:
                output["created"] = result[0]
                output["updated"] = result[1]
        return output

    def execute_initial_lookup_data_task(self):
        with application_context():
            self.load_fixtures_all_data()

    def create_dict(self, qs, key_str="symbol"):
        d = {}
        for entity in qs.all():
            if key_str == "symbol":
                key = entity.symbol.lower()
                d[key] = entity

            if key_str == "name":
                key = entity.symbol.lower()
                d[key] = entity

                key = entity.name.lower()
                d[key] = entity

            if key_str == "equity_index":
                key = f"{entity.equity.symbol}-{entity.index.symbol}".lower()
                d[key] = entity
        return d

    def create_or_update(self, data, entityType):
        if data is None or len(data) == 0:
            return

        records_to_create = [x for x in data if x["id"] is None]
        records_to_update = [x for x in data if x["id"] is not None]
        new_records = [entityType(**values) for values in records_to_create]
        existing_records = [entityType(**values) for values in records_to_update]

        record_keys = list(data[0].keys())
        record_keys.remove("id")
        entityType.backend.bulk_create_or_update(
            new_records, existing_records, record_keys
        )

        return len(records_to_create), len(records_to_update)
