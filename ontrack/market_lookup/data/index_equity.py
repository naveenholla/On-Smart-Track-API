import array
import json
from urllib.request import urlopen

import yaml
from django.conf import settings

from ontrack.market_lookup.queryset import (
    EquityQuerySet,
    ExchangeQuerySet,
    IndexQuerySet,
)

from ...utils.logger import ApplicationLogger


class PullEquityIndexDataPull:
    def __init__(
        self,
        exchange_qs: ExchangeQuerySet = None,
        index_qs: IndexQuerySet = None,
        equity_qs: EquityQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.index_qs = index_qs
        self.equity_qs = equity_qs

    def __get_name_from_weightage_label(
        self, label: str, delimitor: str = " ", maxsplit=1
    ) -> str:
        # remove only the last instance of space
        result = label.rsplit(delimitor, maxsplit)
        return result[0].strip()

    def __process_equity_index_record(
        self, index_symbol: str, record: dict, parent_record: dict = None
    ) -> dict:

        if self.index_qs is None:
            self.logger.log_warning("Index queyset is null.")
            return None

        if self.equity_qs is None:
            self.logger.log_warning("Equity queyset is null.")
            return None

        index = self.index_qs.unique_search(index_symbol).first()
        if index is None:
            self.logger.log_warning(
                f"Index with symbol '{index_symbol}' doesn't exists"
            )
            return None

        equity_symbol = self.__get_name_from_weightage_label(record["label"])
        equity = self.equity_qs.unique_search(equity_symbol).first()
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
