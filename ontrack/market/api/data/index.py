from django.utils.text import slugify

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.models.index import (
    IndexLiveData,
    IndexLiveDerivativeData,
    IndexLiveOpenInterest,
    IndexLiveOptionChain,
)
from ontrack.market.models.lookup import Exchange
from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.filesystem import FileSystemHelper
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper as nh
from ontrack.utils.string import StringHelper

from .common import CommonData


class PullIndexData:
    def __init__(
        self,
        exchange: Exchange = None,
        index_dict: dict = None,
        tp: TaskProgressStatus = None,
    ):
        self.urls = Configurations.get_urls_config()
        self.settings = SettingLogic()

        self.index_dict = index_dict

        self.exchange = exchange
        self.tp = tp

        if exchange:
            self.exchange_symbol = exchange.symbol
            self.timezone = exchange.timezone_name

    def __parse_lookup_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        symbol = record["symbol"].strip().lower()
        strike_diff = (
            record["strike_difference"] if "strike_difference" in record else 0
        )
        chart_symbol = record["chart_symbol"] if "chart_symbol" in record else symbol
        ticker_symbol = (
            record["ticker_symbol"]
            if "ticker_symbol" in record
            else f"^{symbol.upper()}"
        )

        pk = None
        existing_entity = [e for e in self.index_dict if e.symbol.lower() == symbol]
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
        entity["name"] = record["name"]
        entity["symbol"] = symbol
        entity["lot_size"] = lot_size
        entity["chart_symbol"] = chart_symbol
        entity["ticker_symbol"] = ticker_symbol

        entity["ordinal"] = record["ordinal"]
        entity["slug"] = slugify(f"{self.exchange_symbol}_{symbol}")
        entity["is_sectoral"] = record["is_sector"]
        entity["is_active"] = record["is_active"]
        entity["strike_difference"] = strike_diff
        entity["date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_eod_data(self, record):
        # remove extra spaces in the dictionaty keys
        record = {k.strip(): v for (k, v) in record.items()}
        index_name = record["Index Name"].strip().lower()
        date = dt.str_to_datetime(record["Index Date"], "%d-%m-%Y", self.timezone)

        index = [e for e in self.index_dict if e.name.lower() == index_name]
        if len(index) == 0:
            self.tp.log_warning(f"Index '{index_name}' doesn't exists.")
            return None
        index = index[0]

        open_price = nh.str_to_float(record["Open Index Value"])
        high_price = nh.str_to_float(record["High Index Value"])
        low_price = nh.str_to_float(record["Low Index Value"])
        last_price = nh.str_to_float(record["Closing Index Value"])
        close_price = nh.str_to_float(record["Closing Index Value"])
        avg_price = (high_price + low_price) / 2
        price_change = nh.str_to_float(record["Points Change"])
        prev_close = close_price - price_change
        percentage_change = nh.str_to_float(record["Change(%)"])
        traded_quantity = nh.str_to_float(record["Volume"])
        traded_value = nh.str_to_float(record["Turnover (Rs. Cr.)"])
        number_of_trades = None
        quantity_per_trade = None

        index_pe = nh.str_to_float(record["P/E"])
        index_pb = nh.str_to_float(record["P/B"])
        index_div_yield = nh.str_to_float(record["Div Yield"])

        entity = {}
        entity["id"] = None
        entity["entity"] = index
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

        entity["index_pe"] = index_pe
        entity["index_pb"] = index_pb
        entity["index_div_yield"] = index_div_yield

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

        if instrument != InstrumentType.FUTIDX.lower():
            return None

        index = [e for e in self.index_dict if e.symbol.lower() == symbol]
        if len(index) == 0:
            self.tp.log_warning(f"Index '{symbol}' doesn't exists.")
            return None
        index = index[0]

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
        entity["entity"] = index
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

    def __parse_live_data(self, record, date):
        index_name = record["index"].strip().lower()

        index = [e for e in self.index_dict if e.name.lower() == index_name]
        if len(index) == 0:
            self.tp.log_warning(f"Index '{index_name}' doesn't exists.")
            return None
        index = index[0]

        open_price = nh.str_to_float(record["open"])
        high_price = nh.str_to_float(record["high"])
        low_price = nh.str_to_float(record["low"])
        last_price = nh.str_to_float(record["last"])
        prev_close = nh.str_to_float(record["previousClose"])
        close_price = nh.str_to_float(record["last"])
        avg_price = (high_price + low_price) / 2
        price_change = nh.str_to_float(record["variation"])
        percentage_change = nh.str_to_float(record["percentChange"])

        year_high = nh.str_to_float(record["yearHigh"])
        year_low = nh.str_to_float(record["yearLow"])
        one_week_ago = nh.str_to_float(record["oneWeekAgo"])
        one_month_ago = nh.str_to_float(record["oneMonthAgo"])

        declines = nh.str_to_float(record["declines"] if "declines" in record else 0)
        advances = nh.str_to_float(record["advances"] if "advances" in record else 0)
        unchanged = nh.str_to_float(record["unchanged"] if "unchanged" in record else 0)

        price_change_month_ago = nh.str_to_float(record["perChange30d"])
        date_month_ago = dt.str_to_datetime(
            record["date30dAgo"], "%d-%b-%Y", self.timezone
        )
        price_change_year_ago = nh.str_to_float(record["perChange365d"])
        date_year_ago = dt.str_to_datetime(
            record["date365dAgo"], "%d-%b-%Y", self.timezone
        )

        entity = {}
        entity["id"] = None
        entity["entity"] = index
        entity["prev_close"] = prev_close
        entity["open_price"] = open_price
        entity["high_price"] = high_price
        entity["low_price"] = low_price
        entity["last_price"] = last_price
        entity["close_price"] = close_price
        entity["avg_price"] = avg_price
        entity["point_changed"] = price_change
        entity["percentage_changed"] = percentage_change

        entity["declines"] = declines
        entity["advances"] = advances
        entity["unchanged"] = unchanged

        entity["year_high"] = year_high
        entity["year_low"] = year_low
        entity["one_week_ago"] = one_week_ago
        entity["one_month_ago"] = one_month_ago

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

        index = [e for e in self.index_dict if e.symbol.lower() == symbol]
        if len(index) == 0:
            self.tp.log_warning(f"Index '{symbol}' doesn't exists.")
            return None
        index = index[0]

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
        entity["entity"] = index
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
        instrument = InstrumentType.OPTIDX

        index = [e for e in self.index_dict if e.symbol.lower() == symbol]
        if len(index) == 0:
            self.tp.log_warning(f"Index '{symbol}' doesn't exists.")
            return None
        index = index[0]

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
        entity["entity"] = index
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

        index = [e for e in self.index_dict if e.symbol.lower() == symbol]
        if len(index) == 0:
            self.tp.log_warning(f"Index '{symbol}' doesn't exists.")
            return None
        index = index[0]

        lastest_open_interest = nh.str_to_float(record["latestOI"])
        previous_open_interest = nh.str_to_float(record["prevOI"])
        change_in_open_interest = nh.str_to_float(record["changeInOI"])
        average_open_interest = nh.str_to_float(record["avgInOI"])
        volume_open_interest = nh.str_to_float(record["volume"])
        underlying_value = nh.str_to_float(record["underlyingValue"])

        entity = {}
        entity["id"] = None
        entity["entity"] = index
        entity["lastest_open_interest"] = lastest_open_interest
        entity["previous_open_interest"] = previous_open_interest
        entity["change_in_open_interest"] = change_in_open_interest
        entity["average_open_interest"] = average_open_interest
        entity["volume_open_interest"] = volume_open_interest
        entity["underlying_value"] = underlying_value

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def pull_and_parse_lookup_data(self):
        self.tp.log_message("Started with indices.")

        indices_percentage_records = self.urls["indices_percentage"]

        market_cap_url = self.urls["fo_marketlot"]
        commonobj = CommonData()
        self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists.")
            return None

        if indices_percentage_records is None or len(indices_percentage_records) == 0:
            self.tp.log_warning("No index records exists.")
            return None

        entities = []
        for record in indices_percentage_records:
            entity = self.__parse_lookup_data(record)
            entities.append(entity)

        return entities

    def pull_parse_eod_data(self, date):
        url_record = self.urls["index_bhavcopy"]
        url = StringHelper.format_url(url_record, date)
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_pandas_web(url=url)
        data.fillna("0")

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
        self.tp.log_message("Data pull completed.")

        # remove extra spaces from the column names and data
        StringHelper.whitespace_remover(data)

        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_derivative_eod_data(record)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_live_data(self):
        url_record = self.urls["live_index_data"]
        url = url_record["url"]
        self.tp.log_message(f"Started with {url}.")

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return "Exchange is missing."

        # pull csv containing all the listed equities from web
        headers = Configurations.get_header_values_config()
        data = LogicHelper.pull_data_from_external_api(
            record=url_record, headers=headers
        )

        if data is None:
            self.tp.log_warning("No Data Available")
            return "No Data Available."

        entities = []
        date = dt.str_to_datetime(data["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone)

        already_processed = IndexLiveData.backend.filter(date=date).count()
        if already_processed > 0:
            self.tp.log_warning("Already Processed")
            return "Already Processed."

        self.tp.log_message("Data pull completed.")

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
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return "Exchange is missing."

        # pull csv containing all the listed equities from web
        headers = Configurations.get_header_values_config()
        data = LogicHelper.pull_data_from_external_api(
            record=url_record, headers=headers
        )

        self.tp.log_message("Data pull completed.")

        if data is None:
            self.tp.log_warning("No Data Available")
            return "No Data Available."

        entities = []
        date = dt.str_to_datetime(data["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone)

        already_processed = IndexLiveOpenInterest.backend.filter(date=date).count()
        if already_processed > 0:
            self.tp.log_warning("Already Processed")
            return "Already Processed."

        for record in data["data"]:
            entity = self.__parse_live_open_interest(record, date)

            if entity is not None:
                entities.append(entity)

        return entities

    def pull_parse_live_derivative_data(self):
        url_records = self.urls["live_index_future_data"]

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
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

            self.tp.log_message("Data pull completed.")

            if data is None:
                self.tp.log_warning(f"{list_name} - Data is missing.")
                continue

            date = dt.str_to_datetime(
                data["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone
            )

            already_processed = IndexLiveDerivativeData.backend.filter(
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
        url_record = self.urls["live_index_option_chain"]

        if self.exchange is None:
            self.tp.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        headers = Configurations.get_header_values_config()

        entities = []
        for arg in url_record["arg0_options"]:
            url = url_record["url"].replace("{0}", arg.upper().replace("&", "%26"))
            self.tp.log_message(f"Started with {url}.")

            # pull csv containing all the listed equities from web
            data = LogicHelper.pull_data_from_external_api(
                record=url_record, headers=headers, url=url
            )

            self.tp.log_message("Data pull completed.")

            if data is None:
                self.tp.log_warning(f"{arg} - Data is missing.")
                continue

            records = data["records"]

            date = dt.str_to_datetime(
                records["timestamp"], "%d-%b-%Y %H:%M:%S", self.timezone
            )

            already_processed = IndexLiveOptionChain.backend.filter(
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
