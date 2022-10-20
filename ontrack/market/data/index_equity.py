import array
import json
from urllib.request import urlopen

import yaml
from django.conf import settings

from ontrack.market.querysets.lookup import (
    EquityIndexQuerySet,
    EquityQuerySet,
    ExchangeQuerySet,
    IndexQuerySet,
)
from ontrack.utils.logger import ApplicationLogger


class PullEquityIndexDataPull:
    def __init__(
        self,
        exchange_qs: ExchangeQuerySet = None,
        index_qs: IndexQuerySet = None,
        equity_qs: EquityQuerySet = None,
        equityindex_qs: EquityIndexQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.index_qs = index_qs
        self.equity_qs = equity_qs
        self.equityindex_qs = equityindex_qs

    def __get_name_from_label(self, label: str) -> str:
        # remove only the last instance of space
        result = label.rsplit(" ", 1)
        return result[0].strip()

    def __process_record(
        self, index_symbol: str, record: dict, parent: dict = None
    ) -> dict:

        equity_symbol = self.__get_name_from_label(record["label"])
        weight = record["weight"]

        index = self.index_qs.unique_search(index_symbol).first()
        if index is None:
            self.logger.log_warning(
                f"Index with symbol '{index_symbol}' doesn't exists"
            )
            return None

        equity = self.equity_qs.unique_search(equity_symbol).first()
        if equity is None:
            self.logger.log_warning(
                f"Equity with symbol '{equity_symbol}' doesn't exists"
            )
            return None

        pk = None
        existing_entity = self.equityindex_qs.unique_search(
            index_symbol, equity_symbol
        ).first()
        if existing_entity is not None:
            pk = existing_entity.id

        entity = {}
        entity["id"] = pk
        entity["index"] = index
        entity["equity"] = equity
        entity["equity_weightage"] = weight

        if parent is not None:
            label = self.__get_name_from_label(parent["label"])
            weight = parent["weight"]
            entity["sector"] = label
            entity["sector_weightage"] = weight

        return entity

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
        entities = []

        for ogroup in record["groups"]:

            # remove extra spaces in the dictionaty keys
            record = {k.strip(): v for (k, v) in record.items()}

            if "groups" in ogroup:
                for igroup in ogroup["groups"]:
                    entity = self.__process_record(index_name, igroup, ogroup)
                    if entity is not None:
                        entities.append(entity)
            else:
                entity = self.__process_record(index_name, ogroup, None)
                if entity is not None:
                    entities.append(entity)

        return entities
