import re

from django.utils.text import slugify

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.models.equity import (
    EquityLiveData,
    EquityLiveDerivativeData,
    EquityLiveOpenInterest,
    EquityLiveOptionChain,
)
from ontrack.market.models.lookup import Equity, Exchange
from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.filesystem import FileSystemHelper
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper as nh
from ontrack.utils.string import StringHelper

from .common import CommonData


class PullEquityData:
    def __init__(
        self,
        exchange: Exchange = None,
        equity_dict: dict = None,
        tp: TaskProgressStatus = None,
    ):
        self.urls = Configurations.get_urls_config()
        self.settings = SettingLogic()

        self.equity_dict = equity_dict

        self.exchange = exchange
        self.tp = tp

        if exchange:
            self.exchange_symbol = exchange.symbol
            self.timezone = exchange.timezone_name

    def __parse_lookup_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip().lower()
        strike_diff = (
            record["strike_difference"] if "strike_difference" in record else 0
        )
        chart_symbol = record["chart_symbol"] if "chart_symbol" in record else symbol
        ticker_symbol = (
            record["ticker_symbol"]
            if "ticker_symbol" in record
            else f"{symbol.upper()}.NS"
        )

        pk = None
        existing_entity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(existing_entity) > 0:
            existing_entity = existing_entity[0]
            pk = existing_entity.id

            if existing_entity.chart_symbol:
                chart_symbol = existing_entity.chart_symbol

            if existing_entity.ticker_symbol:
                ticker_symbol = existing_entity.ticker_symbol

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
        entity["ticker_symbol"] = ticker_symbol
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["strike_difference"] = strike_diff
        entity["date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_eod_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["SYMBOL"].strip().lower()
        date = dt.str_to_datetime(record["DATE1"], "%d-%b-%Y", self.timezone)
        series = record["SERIES"].strip().lower()

        if series != "eq":
            return None

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            equity = Equity.backend.unique_search(symbol).first()
            if not equity:
                equity = Equity(
                    name=symbol,
                    symbol=symbol,
                    chart_symbol=symbol,
                    ticker_symbol=f"{symbol.upper()}.NS",
                    exchange=self.exchange,
                )
                equity.save()
        else:
            equity = equity[0]

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
        entity["id"] = None
        entity["entity"] = equity
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
        date = dt.str_to_datetime(record["TIMESTAMP"], "%d-%b-%Y", self.timezone)
        expiry_date = dt.str_to_datetime(record["EXPIRY_DT"], "%d-%b-%Y", self.timezone)
        instrument = record["INSTRUMENT"].strip().lower()

        if instrument != InstrumentType.FUTSTK.lower():
            return None

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            return None
        equity = equity[0]

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
        entity["id"] = None
        entity["entity"] = equity
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

    def __parse_corporate_action_data(self, record, date):
        symbol = record["symbol"].strip().lower()
        series = record["series"].strip().lower() if "series" in record else "-"

        if series != "eq":
            return None

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            return None
        equity = equity[0]

        subject = record["subject"]
        exDate = dt.str_to_datetime(record["exDate"], "%d-%b-%Y")
        record_Date = dt.str_to_datetime(record["recDate"], "%d-%b-%Y")
        book_closure_sDate = dt.str_to_datetime(record["bcStartDate"], "%d-%b-%Y")
        book_closure_eDate = dt.str_to_datetime(record["bcEndDate"], "%d-%b-%Y")
        faceVal = nh.str_to_float(record["faceVal"])
        entry_type = "None"

        if subject.lower().__contains__("split"):
            entry_type = "split"
        elif subject.lower().__contains__("bonus"):
            entry_type = "bonus"
        elif subject.lower().__contains__("dividend"):
            entry_type = "dividend"
        else:
            return None

        values = [float(s) for s in re.findall(r"-?\d+\.?\d*", subject)]

        entity = {}
        entity["id"] = None
        entity["entity"] = equity
        entity["symbol"] = symbol
        entity["subject"] = subject
        entity["exDate"] = exDate
        entity["record_Date"] = record_Date
        entity["book_closure_sDate"] = book_closure_sDate
        entity["book_closure_eDate"] = book_closure_eDate
        entity["faceVal"] = faceVal
        entity["entry_type"] = entry_type
        entity["values"] = values

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_live_data(self, record, date):
        symbol = record["symbol"].strip().lower()
        series = record["series"].strip().lower() if "series" in record else "-"

        if series != "eq":
            return None

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            # self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            return None
        equity = equity[0]

        meta = record["meta"]
        industry = meta["industry"].strip() if "industry" in meta else None
        isin_number = meta["isin"].strip() if "isin" in meta else None
        if industry is not None and isin_number is not None:
            if equity.isin_number is None or equity.industry is None:
                equity.isin_number = isin_number
                equity.industry = industry
                equity.save()

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

        price_change_month_ago = None
        if "perChange30d" in record:
            price_change_month_ago = nh.str_to_float(record["perChange30d"])

        date_month_ago = None
        if "date30dAgo" in record:
            date_month_ago = dt.str_to_datetime(
                record["date30dAgo"], "%d-%b-%Y", self.timezone
            )

        price_change_year_ago = None
        if "perChange365d" in record:
            price_change_year_ago = nh.str_to_float(record["perChange365d"])

        date_year_ago = None
        if "date365dAgo" in record:
            date_year_ago = dt.str_to_datetime(
                record["date365dAgo"], "%d-%b-%Y", self.timezone
            )

        entity = {}
        entity["id"] = None
        entity["entity"] = equity
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

    def __parse_live_derivative_data(self, record, date, list_name):
        symbol = record["underlying"].strip().lower()
        instrument = record["instrumentType"]
        expiry_date = dt.str_to_datetime(
            record["expiryDate"], "%d-%b-%Y", self.timezone
        )

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            # self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            return None
        equity = equity[0]

        contract = record["contract"]
        identifier = record["identifier"]
        strike_price = nh.str_to_float(record["strikePrice"])
        ot = OptionType.PE if record["optionType"].lower() == "put" else OptionType.CE
        option_type = ot
        last_price = nh.str_to_float(record["lastPrice"])
        point_changed = nh.str_to_float(record["change"])
        percentage_changed = nh.str_to_float(record["pChange"])
        volumn = nh.str_to_float(record["volume"])
        open_interest = nh.str_to_float(record["openInterest"])
        change_in_open_interest = 0
        no_of_trades = nh.str_to_float(record["noOfTrades"])

        entity = {}
        entity["id"] = None
        entity["entity"] = equity
        entity["instrument"] = instrument
        entity["contract"] = contract
        entity["identifier"] = identifier
        entity["expiry_date"] = expiry_date
        entity["list_type"] = list_name
        entity["strike_price"] = strike_price
        entity["option_type"] = option_type
        entity["last_price"] = last_price
        entity["point_changed"] = point_changed
        entity["percentage_changed"] = percentage_changed
        entity["volumn"] = volumn
        entity["open_interest"] = open_interest
        entity["change_in_open_interest"] = change_in_open_interest
        entity["no_of_trades"] = no_of_trades

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_live_option_chain_pe_ce(self, record, date, option_type):
        symbol = record["underlying"].strip().lower()
        expiry_date = dt.str_to_datetime(
            record["expiryDate"], "%d-%b-%Y", self.timezone
        )
        strike_price = nh.str_to_float(record["strikePrice"])
        instrument = InstrumentType.OPTSTK

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            # self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            return None
        equity = equity[0]

        open_interest = nh.str_to_float(record["openInterest"])
        change_in_open_interest = nh.str_to_float(record["changeinOpenInterest"])
        percentage_change_in_oi = nh.str_to_float(record["pchangeinOpenInterest"])
        total_traded_volume = nh.str_to_float(record["totalTradedVolume"])
        implied_volatility = nh.str_to_float(record["impliedVolatility"])
        last_traded_price = nh.str_to_float(record["lastPrice"])
        change = nh.str_to_float(record["change"])
        percentage_change = nh.str_to_float(record["pChange"])
        total_buy_quantity = nh.str_to_float(record["totalBuyQuantity"])
        total_sell_quantity = nh.str_to_float(record["totalSellQuantity"])
        bid_quantity = nh.str_to_float(record["bidQty"])
        bid_price = nh.str_to_float(record["bidprice"])
        ask_quantity = nh.str_to_float(record["askQty"])
        ask_price = nh.str_to_float(record["askPrice"])

        entity = {}
        entity["id"] = None
        entity["entity"] = equity
        entity["strike_price"] = strike_price
        entity["instrument"] = instrument
        entity["option_type"] = option_type
        entity["expiry_date"] = expiry_date
        entity["open_interest"] = open_interest
        entity["change_in_open_interest"] = change_in_open_interest
        entity["percentage_change_in_oi"] = percentage_change_in_oi

        entity["total_traded_volume"] = total_traded_volume
        entity["implied_volatility"] = implied_volatility
        entity["last_traded_price"] = last_traded_price
        entity["change"] = change
        entity["percentage_change"] = percentage_change
        entity["total_buy_quantity"] = total_buy_quantity
        entity["total_sell_quantity"] = total_sell_quantity
        entity["bid_quantity"] = bid_quantity
        entity["bid_price"] = bid_price
        entity["ask_quantity"] = ask_quantity
        entity["ask_price"] = ask_price

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_live_option_chain(self, record, date, upper_lower_limit):
        strike_price = nh.str_to_float(record["strikePrice"])
        if strike_price < upper_lower_limit[0] or strike_price > upper_lower_limit[1]:
            return None

        pe_entity = self.__parse_live_option_chain_pe_ce(
            record["PE"], date, OptionType.PE
        )
        ce_entity = self.__parse_live_option_chain_pe_ce(
            record["CE"], date, OptionType.CE
        )

        if pe_entity is None or ce_entity is None:
            self.tp.log_warning("PE/CE is not exists.")
            return None

        return pe_entity, ce_entity

    def __parse_live_open_interest(self, record, date):
        symbol = record["symbol"].strip().lower()

        equity = [e for e in self.equity_dict if e.symbol.lower() == symbol]
        if len(equity) == 0:
            # self.tp.log_warning(f"Equity '{symbol}' doesn't exists.")
            return None
        equity = equity[0]

        lastest_open_interest = nh.str_to_float(record["latestOI"])
        previous_open_interest = nh.str_to_float(record["prevOI"])
        change_in_open_interest = nh.str_to_float(record["changeInOI"])
        average_open_interest = nh.str_to_float(record["avgInOI"])
        volume_open_interest = nh.str_to_float(record["volume"])
        future_value = nh.str_to_float(record["futValue"])
        option_value = nh.str_to_float(record["optValue"])
        total_value = nh.str_to_float(record["total"])
        underlying_value = nh.str_to_float(record["underlyingValue"])

        entity = {}
        entity["id"] = None
        entity["entity"] = equity
        entity["lastest_open_interest"] = lastest_open_interest
        entity["previous_open_interest"] = previous_open_interest
        entity["change_in_open_interest"] = change_in_open_interest
        entity["average_open_interest"] = average_open_interest
        entity["volume_open_interest"] = volume_open_interest
        entity["future_value"] = future_value
        entity["option_value"] = option_value
        entity["total_value"] = total_value
        entity["underlying_value"] = underlying_value

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def pull_and_parse_lookup_data(self):
        listing_url = self.urls["listed_equities"]
        self.tp.log_message(f"Started with {listing_url}.")

        market_cap_url = self.urls["fo_marketlot"]
        commonobj = CommonData()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists.")
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
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
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
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
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

    def pull_parse_corporate_action(self, date):
        url_record = self.urls["corporates_actions"]
        url = StringHelper.format_url(url_record, date)
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            return "Exchange is missing."

        # pull csv containing all the listed equities from web
        headers = Configurations.get_header_values_config()
        data = LogicHelper.pull_data_from_external_api(
            record=url_record, headers=headers, url=url
        )

        if data is None:
            return "No Data Available."

        entities = []
        for record in data:
            entity = self.__parse_corporate_action_data(record, date)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_live_data(self):
        url_record = self.urls["live_equity_data"]
        url = url_record["url"]
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            return "Exchange is missing."

        # pull csv containing all the listed equities from web
        headers = Configurations.get_header_values_config()
        data = LogicHelper.pull_data_from_external_api(
            record=url_record, headers=headers
        )

        if data is None or "timestamp" not in data or "data" not in data:
            return "No Data Available."

        entities = []
        date = dt.str_to_datetime(data["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone)

        already_processed = EquityLiveData.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        for record in data["data"]:
            entity = self.__parse_live_data(record, date)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_live_open_interest_data(self):
        url_record = self.urls["live_spurts_oi"]
        url = url_record["url"]
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            return "Exchange is missing."

        # pull csv containing all the listed equities from web
        headers = Configurations.get_header_values_config()
        data = LogicHelper.pull_data_from_external_api(
            record=url_record, headers=headers
        )

        if data is None or "timestamp" not in data or "data" not in data:
            return "No Data Available."

        entities = []
        date = dt.str_to_datetime(data["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone)

        already_processed = EquityLiveOpenInterest.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        for record in data["data"]:
            entity = self.__parse_live_open_interest(record, date)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_live_derivative_data(self):
        url_records = self.urls["live_equity_future_data"]

        if self.exchange is None:
            return "Exchange is missing."

        headers = Configurations.get_header_values_config()

        entities = []
        for url_record in url_records:
            url = url_record["url"]
            list_name = url_record["name"]
            self.tp.log_message(f"Started with {url}.")

            # pull csv containing all the listed equities from web
            data = LogicHelper.pull_data_from_external_api(
                record=url_record, headers=headers
            )

            if data is None or "timestamp" not in data or "data" not in data:
                self.tp.log_warning(f"{list_name} - Data is missing.")
                continue

            date = dt.str_to_datetime(
                data["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone
            )

            already_processed = EquityLiveDerivativeData.backend.filter(
                date=date, list_type__iexact=list_name
            ).count()
            if already_processed > 0:
                self.tp.log_warning(f"{list_name} - Already processed.")
                continue

            for record in data["data"]:
                entity = self.__parse_live_derivative_data(record, date, list_name)

                if entity is not None:
                    entities.append(entity)

        return entities

    def pull_parse_live_option_chain_data(self):
        url_record = self.urls["live_equity_option_chain"]

        if self.exchange is None:
            return "Exchange is missing."

        headers = Configurations.get_header_values_config()

        entities = []
        for arg in url_record["arg0_options"]:
            url = url_record["url"].replace("{0}", arg.upper().replace("&", "%26"))
            self.tp.log_message(f"Started with {url}.")

            # pull csv containing all the listed equities from web
            data = LogicHelper.pull_data_from_external_api(
                record=url_record, headers=headers, url=url
            )

            if data is None or "records" not in data:
                self.tp.log_warning(f"{arg} - Data is missing.")
                continue

            records = data["records"]

            date = dt.str_to_datetime(
                records["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone
            )

            already_processed = EquityLiveOptionChain.backend.filter(
                date=date, entity__symbol__iexact=arg
            ).count()
            if already_processed > 0:
                self.tp.log_warning(f"{arg} - Already processed.")
                continue

            strick_limit = Configurations.get_default_value_by_key(
                "option_chain_strick_price_count"
            )
            strike_prices = records["strikePrices"]
            center = nh.ceil(len(strike_prices) / 2)
            strikeDifference = strike_prices[center] - strike_prices[center - 1]
            price = nh.str_to_float(records["underlyingValue"])
            upper_lower_limit = nh.get_upper_lower_limit(
                price, strikeDifference, strick_limit
            )

            for record in data["filtered"]["data"]:
                entity = self.__parse_live_option_chain(record, date, upper_lower_limit)

                if entity is not None:
                    entities.append(entity[0])
                    entities.append(entity[1])

        return entities
