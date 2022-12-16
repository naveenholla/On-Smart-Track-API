import numpy as np

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt


class BaseLogic:
    def __init__(self):
        self.settings = SettingLogic()

    def can_execute_task(self, date_key, pause_hour_key, default_value_key=None):
        result = self.settings.can_execute_task(
            date_key, pause_hour_key, default_value_key
        )
        next_run_date = result[1]
        next_run_date_str = dt.datetime_to_display_str(result[1])

        if not result[0]:
            message = f"Task is paused for time being till {next_run_date_str}."
            return False, message, next_run_date

        return True, None, next_run_date

    def message_creator(self, module_name, result):
        output = {}
        output["module"] = module_name
        if result is not None:
            if isinstance(result, str):
                output["message"] = result
            elif isinstance(result, list):
                output["records"] = []
                for record in result:
                    output["records"].append(record)
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

    def dictfetchall(self, cursor):
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def calculate_ratio(self, df, a_name, b_name, b_isSum=False):
        a = np.array(df[a_name], dtype=float)
        if not b_isSum:
            b = np.array(df[b_name], dtype=float)
        else:
            b = np.array(df[a_name] + df[b_name], dtype=float)
        r = np.divide(a, b, out=np.zeros_like(a), where=b != 0)
        return np.round(r, 2)
