from django.utils.text import slugify

from ontrack.market.querysets.lookup import ExchangeQuerySet, IndexQuerySet
from ontrack.utils.numbers import NumberHelper

from ...utils.logger import ApplicationLogger
from .common import CommonDataPull


class PullIndexData:
    def __init__(
        self,
        exchange_qs: ExchangeQuerySet,
        index_qs: IndexQuerySet,
        indices_percentage_records,
        market_cap_url: str,
        exchange_symbol: str,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.index_qs = index_qs
        self.exchange_symbol = exchange_symbol
        self.indices_percentage_records = indices_percentage_records

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()
        commonobj = CommonDataPull()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

    def __parse_index_data(self, record):
        symbol = record["symbol"].strip()
        pk = None
        lot_size = 0
        existing_entity = self.index_qs.unique_search(symbol).first()
        if existing_entity is not None:
            pk = existing_entity.id

        market_cap_record = [
            x for x in self.market_cap_records if x["symbol"].lower() == symbol.lower()
        ]
        if len(market_cap_record) > 0:
            lot_size_str = market_cap_record[0]["lot_size"].strip()
            lot_size = NumberHelper.str_to_float(lot_size_str)

        entity = {}
        entity["id"] = pk
        entity["exchange"] = self.exchange
        entity["name"] = record["name"]
        entity["symbol"] = symbol
        entity["chart_symbol"] = (
            record["chart_symbol"] if "chart_symbol" in record else symbol
        )
        entity["lot_size"] = lot_size
        entity["ordinal"] = record["ordinal"]
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["is_sectoral"] = record["is_sector"]
        entity["is_active"] = record["is_active"]
        entity["strike_difference"] = (
            record["strike_difference"] if "strike_difference" in record else 0
        )

        return entity

    def pull_and_parse_indice_data(self):
        self.logger.log_debug("Started with indices.")

        if self.exchange is None:
            self.logger.log_warning(
                f"Exchange with symbol '{self.exchange_symbol}' doesn't exists"
            )
            return None

        if (
            self.indices_percentage_records is None
            or len(self.indices_percentage_records) == 0
        ):
            self.logger.log_warning("No index records exists.")
            return None

        entities = []
        for record in self.indices_percentage_records:
            entity = self.__parse_index_data(record)
            entities.append(entity)

        return entities
