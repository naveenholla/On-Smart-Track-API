from django.utils.text import slugify

from ontrack.market_lookup.queryset import EquityQuerySet, ExchangeQuerySet
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper

from ...utils.logger import ApplicationLogger
from .common import CommonDataPull


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
        self.market_cap_url = market_cap_url
        self.equity_listing_url = equity_listing_url
        self.exchange_symbol = exchange_symbol

    def parse_equity_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip()
        pk = None
        lot_size = 0
        existing_equity = self.equity_qs.unique_search(symbol).first()
        if existing_equity is not None:
            pk = existing_equity.id

        market_cap_record = [
            x for x in self.market_cap_records if x["symbol"].lower() == symbol.lower()
        ]
        if len(market_cap_record) > 0:
            lot_size_str = market_cap_record[0]["lot_size"].strip()
            lot_size = NumberHelper.str_to_float(lot_size_str)

        equity = {}
        equity["id"] = pk
        equity["exchange"] = self.exchange
        equity["name"] = record["NAME OF COMPANY"].strip()
        equity["symbol"] = symbol
        equity["lot_size"] = lot_size
        equity["chart_symbol"] = symbol
        equity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        equity["strike_difference"] = (
            record["strike_difference"] if "strike_difference" in record else 0
        )

        return equity

    def pull_and_parse_equity_data(self):
        self.logger.log_debug(f"Started with {self.equity_listing_url}.")

        self.market_cap_records = CommonDataPull().pull_equity_marketlot_data(
            self.market_cap_url
        )
        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()

        if self.exchange is None:
            self.logger.log_warning(
                f"Exchange with symbol '{self.exchange_symbol}' doesn't exists"
            )
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=self.equity_listing_url)
        equities = []
        for _, record in data.iterrows():
            equity = self.parse_equity_data(record)
            equities.append(equity)

        return equities
