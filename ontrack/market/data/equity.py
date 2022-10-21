from django.utils.text import slugify

from ontrack.market.querysets.lookup import EquityQuerySet, ExchangeQuerySet
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper

from .common import CommonData


class PullEquityData:
    def __init__(
        self,
        exchange_qs: ExchangeQuerySet,
        equity_qs: EquityQuerySet,
        equity_listing_url: str,
        market_cap_url: str,
        exchange_symbol: str,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.equity_qs = equity_qs
        self.equity_listing_url = equity_listing_url
        self.exchange_symbol = exchange_symbol

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()
        commonobj = CommonData()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

    def __parse_equity_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip()

        pk = None
        existing_entity = self.equity_qs.unique_search(symbol).first()
        if existing_entity is not None:
            pk = existing_entity.id

        lot_size = 0
        market_cap_record = [
            x for x in self.market_cap_records if x["symbol"].lower() == symbol.lower()
        ]
        if len(market_cap_record) > 0:
            lot_size_str = market_cap_record[0]["lot_size"].strip()
            lot_size = NumberHelper.str_to_float(lot_size_str)

        entity = {}
        entity["id"] = pk
        entity["exchange"] = self.exchange
        entity["name"] = record["NAME OF COMPANY"].strip()
        entity["symbol"] = symbol
        entity["lot_size"] = lot_size
        entity["chart_symbol"] = symbol
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["strike_difference"] = (
            record["strike_difference"] if "strike_difference" in record else 0
        )

        return entity

    def pull_and_parse_equity_data(self):
        self.logger.log_debug(f"Started with {self.equity_listing_url}.")

        if self.exchange is None:
            self.logger.log_warning(
                f"Exchange with symbol '{self.exchange_symbol}' doesn't exists"
            )
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=self.equity_listing_url)
        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_equity_data(record)
            entities.append(entity)

        return entities
