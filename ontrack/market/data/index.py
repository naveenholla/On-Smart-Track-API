from django.utils.text import slugify

from ontrack.market.querysets.lookup import ExchangeQuerySet, IndexQuerySet
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.numbers import NumberHelper

from .common import CommonData


class PullIndexData:
    def __init__(
        self,
        exchange_symbol: str,
        exchange_qs: ExchangeQuerySet = None,
        index_qs: IndexQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.index_qs = index_qs
        self.exchange_symbol = exchange_symbol

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()

        urls = Configurations.get_urls_config()
        self.indices_percentage_records = urls["indices_percentage"]
        market_cap_url = urls["fo_marketlot"]

        commonobj = CommonData()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

    def __parse_index_data(self, record):
        symbol = record["symbol"].strip().lower()
        strike_diff = (
            record["strike_difference"] if "strike_difference" in record else 0
        )
        chart_symbol = record["chart_symbol"] if "chart_symbol" in record else symbol

        pk = None
        existing_entity = self.index_qs.unique_search(symbol).first()
        if existing_entity is not None:
            pk = existing_entity.id

        lot_size = 0
        mcr = [x for x in self.market_cap_records if x["symbol"] == symbol]
        if len(mcr) > 0:
            lot_size_str = mcr[0]["lot_size"].strip()
            lot_size = NumberHelper.str_to_float(lot_size_str)

        entity = {}
        entity["id"] = pk
        entity["exchange"] = self.exchange
        entity["name"] = record["name"]
        entity["symbol"] = symbol
        entity["chart_symbol"] = chart_symbol
        entity["lot_size"] = lot_size
        entity["ordinal"] = record["ordinal"]
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["is_sectoral"] = record["is_sector"]
        entity["is_active"] = record["is_active"]
        entity["strike_difference"] = strike_diff
        entity["updated_at"] = dt.current_date_time()

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
