from django.utils.text import slugify

from ontrack.market.querysets.equity import (
    EquityDerivativeEndOfDayQuerySet,
    EquityEndOfDayQuerySet,
    EquityLiveDataQuerySet,
)
from ontrack.market.querysets.lookup import EquityQuerySet, ExchangeQuerySet
from ontrack.utils.base.enum import InstrumentType
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.filesystem import FileSystemHelper
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
        equity_derivative_eod_qs: EquityDerivativeEndOfDayQuerySet = None,
        equity_live_qs: EquityLiveDataQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.equity_qs = equity_qs
        self.equity_eod_qs = equity_eod_qs
        self.equity_derivative_eod_qs = equity_derivative_eod_qs
        self.equity_live_qs = equity_live_qs

        self.equity_eod_qs = equity_eod_qs
        self.exchange_symbol = exchange_symbol

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()
        self.urls = Configurations.get_urls_config()

    def __parse_lookup_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip().lower()
        strike_diff = (
            record["strike_difference"] if "strike_difference" in record else 0
        )
        chart_symbol = record["chart_symbol"] if "chart_symbol" in record else symbol

        pk = None
        existing_entity = self.equity_qs.unique_search(symbol).first()
        if existing_entity is not None:
            pk = existing_entity.id

        lot_size = 0
        mcr = [x for x in self.market_cap_records if x["symbol"] == symbol]
        if len(mcr) > 0:
            lot_size_str = mcr[0]["lot_size"].strip()
            lot_size1_str = mcr[0]["lot_size1"].strip()
            lot_size = nh.str_to_float(lot_size_str)
            if lot_size == 0:
                lot_size = nh.str_to_float(lot_size1_str)

        entity = {}
        entity["id"] = pk
        entity["exchange"] = self.exchange
        entity["name"] = record["NAME OF COMPANY"].strip()
        entity["symbol"] = symbol
        entity["lot_size"] = lot_size
        entity["chart_symbol"] = chart_symbol
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["strike_difference"] = strike_diff
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_eod_data(self, record):
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

    def __parse_derivative_eod_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip().lower()
        date = dt.string_to_datetime(record["TIMESTAMP"], "%d-%b-%Y")
        expiry_date = dt.string_to_datetime(record["EXPIRY_DT"], "%d-%b-%Y")
        instrument = record["INSTRUMENT"].strip().lower()

        if instrument != InstrumentType.FUTSTK.lower():
            return None

        equity = self.equity_qs.unique_search(symbol).first()
        if equity is None:
            return None

        pk = None
        existing_entity = self.equity_derivative_eod_qs.unique_search(
            date, equity_id=equity.id, expiry_date=expiry_date
        ).first()
        if existing_entity is not None:
            pk = existing_entity.id

        open_price = nh.str_to_float(record["OPEN"])
        high_price = nh.str_to_float(record["HIGH"])
        low_price = nh.str_to_float(record["LOW"])
        last_price = nh.str_to_float(record["SETTLE_PR"])
        prev_close = 0
        close_price = nh.str_to_float(record["CLOSE"])
        avg_price = (high_price + low_price) / 2
        price_change = 0
        percentage_change = 0
        strike_price = None
        option_type = None
        no_of_contracts = nh.str_to_float(record["CONTRACTS"])
        value_of_contracts = nh.str_to_float(record["VAL_INLAKH"])
        open_interest = nh.str_to_float(record["OPEN_INT"])
        change_in_open_interest = nh.str_to_float(record["CHG_IN_OI"])

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

        entity["instrument"] = instrument
        entity["expiry_date"] = expiry_date
        entity["strike_price"] = strike_price
        entity["option_type"] = option_type
        entity["no_of_contracts"] = no_of_contracts
        entity["value_of_contracts"] = value_of_contracts
        entity["open_interest"] = open_interest
        entity["change_in_open_interest"] = change_in_open_interest

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_live_data(self, record):
        symbol = record["symbol"].strip().lower()
        series = record["series"].strip().lower() if "series" in record else "-"

        if series != "eq":
            return None

        equity = self.equity_qs.unique_search(symbol).first()
        if equity is None:
            return None

        meta = record["meta"]
        industry = meta["industry"].strip().lower() if "industry" in meta else None
        isin_number = meta["isin"].strip().lower() if "isin" in meta else None
        date = dt.string_to_datetime(record["lastUpdateTime"], "%d-%b-%Y %H:%M:%S")

        if industry is not None and isin_number is not None:
            if equity.isin_number is None or equity.industry is None:
                equity.isin_number = isin_number
                equity.industry = industry
                equity.save()

        pk = None
        existing_entity = self.equity_live_qs.unique_search(
            date, equity_id=equity.id
        ).first()
        if existing_entity is not None:
            pk = existing_entity.id

        open_price = nh.str_to_float(record["open"])
        high_price = nh.str_to_float(record["dayHigh"])
        low_price = nh.str_to_float(record["dayLow"])
        last_price = nh.str_to_float(record["lastPrice"])
        prev_close = nh.str_to_float(record["previousClose"])
        close_price = nh.str_to_float(record["lastPrice"])
        avg_price = (high_price + low_price) / 2
        price_change = nh.str_to_float(record["change"])
        percentage_change = nh.str_to_float(record["pChange"])

        traded_quantity = nh.str_to_float(record["totalTradedVolume"])
        traded_value = nh.str_to_float(record["totalTradedValue"])
        number_of_trades = None
        quantity_per_trade = None

        year_high = nh.str_to_float(record["yearHigh"])
        year_low = nh.str_to_float(record["yearLow"])
        near_week_high = nh.str_to_float(record["nearWKH"])
        near_week_low = nh.str_to_float(record["nearWKL"])

        price_change_month_ago = nh.str_to_float(record["perChange30d"])
        date_month_ago = dt.string_to_datetime(record["date30dAgo"], "%d-%b-%Y")
        price_change_year_ago = nh.str_to_float(record["perChange365d"])
        date_year_ago = dt.string_to_datetime(record["date365dAgo"], "%d-%b-%Y")

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

        entity["year_high"] = year_high
        entity["year_low"] = year_low
        entity["near_week_high"] = near_week_high
        entity["near_week_low"] = near_week_low

        entity["price_change_month_ago"] = price_change_month_ago
        entity["date_month_ago"] = date_month_ago
        entity["price_change_year_ago"] = price_change_year_ago
        entity["date_year_ago"] = date_year_ago

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def pull_and_parse_lookup_data(self):
        listing_url = self.urls["listed_equities"]
        self.logger.log_debug(f"Started with {listing_url}.")

        market_cap_url = self.urls["fo_marketlot"]
        commonobj = CommonData()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=listing_url)
        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_lookup_data(record)
            entities.append(entity)

        return entities

    def pull_parse_eod_data(self, date):
        url_record = self.urls["equity_bhavcopy"]
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
            entity = self.__parse_eod_data(record)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_derivative_eod_data(self, date):
        url_record = self.urls["fo_bhavcopy"]
        url = StringHelper.format_url(url_record, date)
        self.logger.log_debug(f"Started with {url}.")

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        temp_folder = FileSystemHelper.create_temp_folder("fo")
        file_name = FileSystemHelper.download_extract_zip(url, temp_folder)
        path = temp_folder / file_name

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas(path=path)

        # remove extra spaces from the column names and data
        StringHelper.whitespace_remover(data)

        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_derivative_eod_data(record)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_live_data(self):
        url_record = self.urls["live_equity_data"]
        url = url_record["url"]
        self.logger.log_debug(f"Started with {url}.")

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        # pull csv containing all the listed equities from web
        headers = Configurations.get_header_values_config()
        data = LogicHelper.pull_data_from_external_api(
            record=url_record, headers=headers
        )

        if data is None:
            return None

        entities = []
        for record in data["data"]:
            entity = self.__parse_live_data(record)

            if entity is not None:
                entities.append(entity)

        return entities
