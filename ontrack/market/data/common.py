import os

from django.conf import settings
from django.core.management import call_command

from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper


class CommonData:
    def __init__(self):
        self.logger = ApplicationLogger()

    def create_temp_folder(self, folder_name, temp_folder_path=None):
        if temp_folder_path is None:
            temp_folder_path = settings.TEMP_DIR

        # temp folder to store files
        fixtures_dir = temp_folder_path / folder_name
        if not os.path.exists(fixtures_dir):
            fixtures_dir.mkdir()
        return fixtures_dir

    def load_lookup_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
        ]

        temp_folder = self.create_temp_folder("fixtures", temp_folder_path)

        app_folder = settings.APPS_FOLDER_NAME

        for fixture in fixtures:
            fixture_details = fixture.split(".")
            app_name = fixture_details[0]
            model = fixture_details[1]
            source = f"{app_folder}/{app_name}/fixtures/{model}.json"
            destination = temp_folder / f"{model}.json"
            print(source)
            print(destination)

            with open(source, "rb") as f:
                data = f.read()

            with open(destination, "wb") as f_new:
                f_new.write(data)

            call_command("loaddata", destination)

    def pull_marketlot_data(self, url: str):
        self.logger.log_debug(f"Started with {url}.")

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=url)
        data.columns.values[2] = "lot_size"
        market_caps = []
        for _, record in data.iterrows():

            # remove extra spaces in the dictionaty keys
            record = {k.strip(): v for (k, v) in record.items()}
            market_cap = {}
            market_cap["symbol"] = record["SYMBOL"].strip().lower()
            market_cap["lot_size"] = record["lot_size"].strip()

            market_caps.append(market_cap)

        return market_caps

    def create_or_update(self, data, entityType, manager):
        if data is None or len(data) == 0:
            return

        records_to_create = [x for x in data if x["id"] is None]
        records_to_update = [x for x in data if x["id"] is not None]
        new_records = [entityType(**values) for values in records_to_create]
        existing_records = [entityType(**values) for values in records_to_update]

        record_keys = list(data[0].keys())
        record_keys.remove("id")
        manager.bulk_create_or_update(new_records, existing_records, record_keys)
