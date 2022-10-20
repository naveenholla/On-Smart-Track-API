import array
import json
from urllib.request import urlopen

import yaml
from django.conf import settings
from django.utils.text import slugify

from ontrack.market_lookup.queryset import (
    EquityQuerySet,
    ExchangeQuerySet,
    IndexQuerySet,
)
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper

from ...utils.logger import ApplicationLogger


class PullEquityData:
    def __init__(
        self,
        exchange_queryset: ExchangeQuerySet = None,
        equity_queryset: EquityQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_queryset = exchange_queryset
        self.equity_queryset = equity_queryset

    def pull_and_parse_equity_data(
        self, exchange_symbol: str, url: str, market_cap_url: str
    ):
        self.logger.log_debug(f"Started with {url}.")

        if url is None or market_cap_url is None:
            self.logger.log_debug("url and market_cap_url is required.")
            return None

        if self.exchange_queryset is None:
            self.logger.log_warning("Exchange queyset is null.")
            return None

        exchange = self.exchange_queryset.search_unique_record(exchange_symbol).first()

        if exchange is None:
            self.logger.log_warning(
                f"Exchange with symbol '{exchange_symbol}' doesn't exists"
            )
            return None

        market_cap_records = self.pull_equity_marketlot_data(market_cap_url)

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=url)
        equities = []
        for _, record in data.iterrows():

            # remove extra spaces in the dictionaty keys
            record = {k.strip(): v for (k, v) in record.items()}
            symbol = record["SYMBOL"].strip()
            pk = None
            lot_size = 0
            existing_equity = self.equity_queryset.search_unique_record(symbol).first()
            if existing_equity is not None:
                pk = existing_equity.id

            market_cap_record = [
                x for x in market_cap_records if x["symbol"].lower() == symbol.lower()
            ]
            if len(market_cap_record) > 0:
                lot_size = NumberHelper.convert_string_to_float(
                    market_cap_record[0]["lot_size"].strip()
                )

            equity = {}
            equity["id"] = pk
            equity["exchange"] = exchange
            equity["name"] = record["NAME OF COMPANY"].strip()
            equity["symbol"] = symbol
            equity["lot_size"] = lot_size
            equity["chart_symbol"] = symbol
            equity["slug"] = slugify(f"{exchange_symbol}_{symbol}")
            equity["strike_difference"] = (
                record["strike_difference"] if "strike_difference" in record else 0
            )

            equities.append(equity)

        return equities

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


class PullIndexData:
    def __init__(
        self,
        exchange_queryset: ExchangeQuerySet = None,
        index_queryset: IndexQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_queryset = exchange_queryset
        self.index_queryset = index_queryset

    def pull_index_marketlot_data(self, url: str):
        return PullEquityData().pull_equity_marketlot_data(url)

    def parse_index_data(self, exchange_symbol: str, record: dict, market_cap_url: str):
        if self.exchange_queryset is None:
            self.logger.log_warning("Exchange queyset is null.")
            return None

        exchange = self.exchange_queryset.search_unique_record(exchange_symbol).first()
        if exchange is None:
            self.logger.log_warning(
                f"Exchange with symbol '{exchange_symbol}' doesn't exists"
            )
            return None

        market_cap_records = self.pull_equity_marketlot_data(market_cap_url)

        symbol = record["symbol"]
        pk = None
        lot_size = record["lot_size"] if "lot_size" in record else 0
        existing_index = self.index_queryset.search_unique_record(symbol).first()
        if existing_index is not None:
            pk = existing_index.id

        market_cap_record = [x for x in market_cap_records if x["symbol"] == symbol]
        if len(market_cap_record) > 0:
            lot_size = market_cap_record[0]["lot_size"]

        dict_record = {}
        dict_record["id"] = pk
        dict_record["exchange"] = {"symbol": exchange_symbol}
        dict_record["name"] = record["name"]
        dict_record["symbol"] = record["symbol"]
        dict_record["chart_symbol"] = (
            record["chart_symbol"] if "chart_symbol" in record else record["symbol"]
        )
        dict_record["lot_size"] = lot_size
        dict_record["ordinal"] = record["ordinal"]
        dict_record["slug"] = slugify(f"{exchange_symbol}_{record['symbol']}")
        dict_record["is_sectoral"] = record["is_sector"]
        dict_record["is_active"] = record["is_active"]
        dict_record["strike_difference"] = (
            record["strike_difference"] if "strike_difference" in record else 0
        )

        return dict_record


class PullEquityIndexDataPull:
    def __init__(
        self,
        exchange_queryset: ExchangeQuerySet = None,
        index_queryset: IndexQuerySet = None,
        equity_queryset: EquityQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_queryset = exchange_queryset
        self.index_queryset = index_queryset
        self.equity_queryset = equity_queryset

    def __get_name_from_weightage_label(
        self, label: str, delimitor: str = " ", maxsplit=1
    ) -> str:
        # remove only the last instance of space
        result = label.rsplit(delimitor, maxsplit)
        return result[0].strip()

    def __process_equity_index_record(
        self, index_symbol: str, record: dict, parent_record: dict = None
    ) -> dict:

        if self.index_queryset is None:
            self.logger.log_warning("Index queyset is null.")
            return None

        if self.equity_queryset is None:
            self.logger.log_warning("Equity queyset is null.")
            return None

        index = self.index_queryset.search_unique_record(index_symbol).first()
        if index is None:
            self.logger.log_warning(
                f"Index with symbol '{index_symbol}' doesn't exists"
            )
            return None

        equity_symbol = self.__get_name_from_weightage_label(record["label"])
        equity = self.equity_queryset.search_unique_record(equity_symbol).first()
        if equity is None:
            self.logger.log_warning(
                f"Equity with symbol '{equity_symbol}' doesn't exists"
            )
            return None

        dict_record = {}
        dict_record["index"] = index
        dict_record["equity"] = equity
        dict_record["equity_weightage"] = record["weight"]

        if parent_record is not None:
            dict_record["sector"] = self.__get_name_from_weightage_label(
                parent_record["label"]
            )
            dict_record["sector_weightage"] = record["weight"]

        return dict_record

    def pull_indices_market_cap(self, record: dict):
        temp_folder = settings.TEMP_DIR  # temp folder to store files

        if "url" not in record:
            self.logger.log_debug("No url exists for '%s'." % record["name"])
            return None

        # get indices details
        index_url = record["url"]
        index_name = str(record["name"])
        sector_name_file_name = index_name.replace(" ", "_")

        self.logger.log_debug(f"Started with {index_name}, {index_url}.")
        with urlopen(index_url) as webpage:
            content = (
                webpage.read()
                .decode()
                .replace("'", "||||")
                .replace("modelDataAvailable(", "[")
                .replace(");", "]")
                .replace("label:", '"label":')
                .replace("label:", '"label":')
                .replace("file:", '"file":')
            )

            url_temp = f"{temp_folder}/{sector_name_file_name}_temp.json"

            with open(url_temp, "w") as file_intermediate:
                # Writing the replaced data in our
                # text file
                file_intermediate.write(
                    json.dumps(content, ensure_ascii=True, indent=4).replace(
                        '\\"', '"'
                    )[1:-1]
                )

            with open(url_temp) as file_intermediate2:
                # Writing the replaced data in our
                # text file
                data = yaml.safe_load(file_intermediate2)

            with open(url_temp, "w") as file_final:
                # Writing the replaced data in our
                # text file
                file_final.write(str(data).replace("'", '"').replace("||||", "'"))

            with open(url_temp) as file_final2:
                # Writing the replaced data in our
                # text file
                return json.load(file_final2)

    def parse_indices_market_cap(self, index_name: str, record: dict) -> array:
        equities = []

        for outer_group in record["groups"]:

            # remove extra spaces in the dictionaty keys
            record = {k.strip(): v for (k, v) in record.items()}

            if "groups" in outer_group:
                for inner_group in outer_group["groups"]:
                    equity = self.__process_equity_index_record(
                        index_name, inner_group, outer_group
                    )
                    if equity is not None:
                        equities.append(equity)
            else:
                equity = self.__process_equity_index_record(
                    index_name, outer_group, None
                )
                if equity is not None:
                    equities.append(equity)

        return equities
