from django.utils.text import slugify

from ontrack.market.querysets.equity import EquityEndOfDayQuerySet
from ontrack.market.querysets.lookup import EquityQuerySet, ExchangeQuerySet
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper as nh
from ontrack.utils.string import StringHelper

from .common import CommonData


class PullEquityData:
    def __init__(
        self,
        exchange_symbol: str,
        exchange_qs: ExchangeQuerySet = None,
        equity_qs: EquityQuerySet = None,
        equity_eod_qs: EquityEndOfDayQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.equity_qs = equity_qs
        self.equity_eod_qs = equity_eod_qs
        self.exchange_symbol = exchange_symbol

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()

        urls = Configurations.get_urls_config()
        self.equity_listing_url = urls["listed_equities"]
        market_cap_url = urls["fo_marketlot"]
        self.eod_format_url = urls["equity_bhavcopy"]

        commonobj = CommonData()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

    def __parse_equity_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip().lower()
        strike_diff = (
            record["strike_difference"] if "strike_difference" in record else 0
        )

        pk = None
        existing_entity = self.equity_qs.unique_search(symbol).first()
        if existing_entity is not None:
            pk = existing_entity.id

        lot_size = 0
        mcr = [x for x in self.market_cap_records if x["symbol"] == symbol]
        if len(mcr) > 0:
            lot_size_str = mcr[0]["lot_size"].strip()
            lot_size = nh.str_to_float(lot_size_str)

        entity = {}
        entity["id"] = pk
        entity["exchange"] = self.exchange
        entity["name"] = record["NAME OF COMPANY"].strip()
        entity["symbol"] = symbol
        entity["lot_size"] = lot_size
        entity["chart_symbol"] = symbol
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["strike_difference"] = strike_diff
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_equity_eod_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip().lower()
        date = dt.string_to_datetime(record["DATE1"], "%d-%b-%Y")
        series = record["SERIES"].strip().lower()

        if series != "eq":
            return None

        equity = self.equity_qs.unique_search(symbol).first()
        if equity is None:
            return None

        pk = None
        existing_entity = self.equity_eod_qs.unique_search(
            date, equity_id=equity.id
        ).first()
        if existing_entity is not None:
            pk = existing_entity.id

        open_price = nh.str_to_float(record["OPEN_PRICE"])
        high_price = nh.str_to_float(record["HIGH_PRICE"])
        low_price = nh.str_to_float(record["LOW_PRICE"])
        last_price = nh.str_to_float(record["LAST_PRICE"])
        prev_close = nh.str_to_float(record["PREV_CLOSE"])
        close_price = nh.str_to_float(record["CLOSE_PRICE"])
        avg_price = nh.str_to_float(record["AVG_PRICE"])
        price_change = close_price - prev_close
        percentage_change = price_change / close_price * 100
        traded_quantity = nh.str_to_float(record["TTL_TRD_QNTY"])
        traded_value = nh.str_to_float(record["TURNOVER_LACS"])
        number_of_trades = nh.str_to_float(record["NO_OF_TRADES"])
        quantity_per_trade = traded_quantity / number_of_trades

        delivery_quantity = nh.str_to_float(record["DELIV_QTY"])
        delivery_percentage = nh.str_to_float(record["DELIV_PER"])

        entity = {}
        entity["id"] = pk
        entity["equity"] = equity
        entity["prev_close"] = prev_close
        entity["open_price"] = open_price
        entity["high_price"] = high_price
        entity["low_price"] = low_price
        entity["last_price"] = last_price
        entity["close_price"] = close_price
        entity["avg_price"] = avg_price
        entity["point_changed"] = price_change
        entity["percentage_changed"] = percentage_change
        entity["traded_quantity"] = traded_quantity
        entity["traded_value"] = traded_value
        entity["number_of_trades"] = number_of_trades
        entity["quantity_per_trade"] = quantity_per_trade
        entity["delivery_quantity"] = delivery_quantity
        entity["delivery_percentage"] = delivery_percentage
        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def pull_and_parse_equity_data(self):
        self.logger.log_debug(f"Started with {self.equity_listing_url}.")

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=self.equity_listing_url)
        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_equity_data(record)
            entities.append(entity)

        return entities

    def pull_parse_equity_eod_data(self, date):
        url_record = self.eod_format_url
        url = StringHelper.format_url(url_record, date)
        self.logger.log_debug(f"Started with {url}.")

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=url)

        # remove extra spaces from the column names and data
        StringHelper.whitespace_remover(data)

        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_equity_eod_data(record)

            if entity is not None:
                entities.append(entity)

        return entities
