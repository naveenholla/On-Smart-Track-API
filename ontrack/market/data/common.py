from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper


class CommonData:
    def __init__(self):
        self.logger = ApplicationLogger()

    def pull_marketlot_data(self, url: str):
        self.logger.log_debug(f"Started with {url}.")

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=url)
        data.columns.values[2] = "lot_size"
        data.columns.values[3] = "lot_size1"
        data.columns.values[4] = "lot_size2"
        market_caps = []
        for _, record in data.iterrows():

            # remove extra spaces in the dictionaty keys
            record = {k.strip(): v for (k, v) in record.items()}
            market_cap = {}
            market_cap["symbol"] = record["SYMBOL"].strip().lower()
            market_cap["lot_size"] = record["lot_size"].strip()
            market_cap["lot_size1"] = record["lot_size1"].strip()
            market_cap["lot_size2"] = record["lot_size2"].strip()

            market_caps.append(market_cap)

        return market_caps

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
