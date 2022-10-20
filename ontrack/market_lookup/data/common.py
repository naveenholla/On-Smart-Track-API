from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper


class CommonDataPull:
    def __init__(self):
        self.logger = ApplicationLogger()

    def pull_equity_marketlot_data(self, url: str):
        self.logger.log_debug(f"Started with {url}.")

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=url)
        data.columns.values[2] = "lot_size"
        market_caps = []
        for _, record in data.iterrows():

            # remove extra spaces in the dictionaty keys
            record = {k.strip(): v for (k, v) in record.items()}
            market_cap = {}
            market_cap["symbol"] = record["SYMBOL"].strip()
            market_cap["lot_size"] = record["lot_size"].strip()

            market_caps.append(market_cap)

        return market_caps
