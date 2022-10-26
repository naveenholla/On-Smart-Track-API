import pandas as pd

from ontrack.market.querysets.lookup import ExchangeQuerySet
from ontrack.market.querysets.participant import (
    ParticipantActivityQuerySet,
    ParticipantStatsActivityQuerySet,
)
from ontrack.utils.base.enum import ClientType, InstrumentType, OptionType
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper as nh
from ontrack.utils.string import StringHelper


class PullParticipantData:
    def __init__(
        self,
        exchange_symbol: str,
        exchange_qs: ExchangeQuerySet = None,
        participant_qs: ParticipantActivityQuerySet = None,
        participant_stats_qs: ParticipantStatsActivityQuerySet = None,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.participant_qs = participant_qs
        self.participant_stats_qs = participant_stats_qs
        self.exchange_symbol = exchange_symbol

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()
        self.urls = Configurations.get_urls_config()

        self.client_type = {
            value.lower(): key.lower() for key, value in ClientType.choices
        }

        self.instrument_mapping = {
            "INDEX FUTURES": InstrumentType.FUTIDX,
            "INDEX OPTIONS": InstrumentType.OPTIDX,
            "STOCK FUTURES": InstrumentType.FUTSTK,
            "STOCK OPTIONS": InstrumentType.OPTSTK,
        }

    def __parse_eod_record(
        self, date, client_type, instrument, option_type, long_value, short_value
    ):
        filter = {
            "date": date,
            "client_type": client_type,
            "instrument": instrument,
            "option_type": option_type,
        }

        pk = None
        existing_entity = self.participant_qs.unique_search(**filter).first()
        if existing_entity is not None:
            pk = existing_entity.id

        buy_amount = nh.str_to_float(long_value)
        sell_amount = nh.str_to_float(short_value)
        net_amount = buy_amount - sell_amount

        entity = {}
        entity["id"] = pk
        entity["client_type"] = client_type
        entity["instrument"] = instrument
        entity["option_type"] = option_type
        entity["buy_amount"] = buy_amount
        entity["sell_amount"] = sell_amount
        entity["net_amount"] = net_amount

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_eod_stats_record(self, date, record):
        client_type = ClientType.FII
        instrument = self.instrument_mapping[record["instrument"]]
        filter = {
            "date": date,
            "client_type": client_type,
            "instrument": instrument,
        }

        pk = None
        existing_entity = self.participant_stats_qs.unique_search(**filter).first()
        if existing_entity is not None:
            pk = existing_entity.id

        entity = {}
        entity["id"] = pk
        entity["client_type"] = client_type
        entity["instrument"] = instrument
        entity["no_of_contracts_bought"] = nh.str_to_float(
            record["no_of_contracts_bought"]
        )
        entity["value_of_contracts_bought"] = nh.str_to_float(
            record["value_of_contracts_bought"]
        )
        entity["no_of_contracts_sold"] = nh.str_to_float(record["no_of_contracts_sold"])
        entity["value_of_contracts_sold"] = nh.str_to_float(
            record["value_of_contracts_sold"]
        )
        entity["open_interest"] = nh.str_to_float(record["open_interest"])
        entity["value_of_open_interest"] = nh.str_to_float(
            record["value_of_open_interest"]
        )

        entity["date"] = date
        entity["pull_date"] = dt.current_date_time()
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __parse_eod_data(self, date, record):
        # remove extra spaces in the dictionaty keys
        client_type_str = record["Client Type"].strip().lower()

        result_records = []
        if client_type_str not in self.client_type:
            return result_records

        client_type = self.client_type[client_type_str].upper()

        instrument = InstrumentType.FUTIDX
        option_type = None
        long_value = record["Future Index Long"]
        short_value = record["Future Index Short"]
        result_record = self.__parse_eod_record(
            date, client_type, instrument, option_type, long_value, short_value
        )
        result_records.append(result_record)

        instrument = InstrumentType.FUTSTK
        option_type = None
        long_value = record["Future Stock Long"]
        short_value = record["Future Stock Short"]
        result_record = self.__parse_eod_record(
            date, client_type, instrument, option_type, long_value, short_value
        )
        result_records.append(result_record)

        instrument = InstrumentType.OPTIDX
        option_type = OptionType.CE
        long_value = record["Option Index Call Long"]
        short_value = record["Option Index Call Short"]
        result_record = self.__parse_eod_record(
            date, client_type, instrument, option_type, long_value, short_value
        )
        result_records.append(result_record)

        instrument = InstrumentType.OPTIDX
        option_type = OptionType.PE
        long_value = record["Option Index Put Long"]
        short_value = record["Option Index Put Short"]
        result_record = self.__parse_eod_record(
            date, client_type, instrument, option_type, long_value, short_value
        )
        result_records.append(result_record)

        instrument = InstrumentType.OPTSTK
        option_type = OptionType.CE
        long_value = record["Option Stock Call Long"]
        short_value = record["Option Stock Call Short"]
        result_record = self.__parse_eod_record(
            date, client_type, instrument, option_type, long_value, short_value
        )
        result_records.append(result_record)

        instrument = InstrumentType.OPTSTK
        option_type = OptionType.PE
        long_value = record["Option Stock Put Long"]
        short_value = record["Option Stock Put Short"]
        result_record = self.__parse_eod_record(
            date, client_type, instrument, option_type, long_value, short_value
        )
        result_records.append(result_record)

        return result_records

    def __parse_participant_cash(self, date):
        url_format = self.urls["participant_activity"]["cash"]
        url = StringHelper.format_url(url_format, date)

        df = pd.read_html(url)[0]
        df.columns = df.columns.map("-".join).str.strip("-")

        columns = []
        for column in df.columns:
            c = (
                column.rsplit("-", 1)[0]
                .replace("Unnamed: 0_level_0-", "")
                .replace(" Rs Crores-", " ")
                .replace("-", "")
            )
            columns.append(c)
        df.columns = columns

        date_str = dt.convert_datetime_to_string(date, "%d-%b-%Y")

        result_records = []

        for _, record in df.iterrows():
            if record["Date"] != date_str:
                continue

            client_type = ClientType.FII
            instrument = InstrumentType.CASH
            long_value = record["FII Gross Purchase"]
            short_value = record["FII Gross Sales"]
            result_record = self.__parse_eod_record(
                date, client_type, instrument, None, long_value, short_value
            )
            result_records.append(result_record)

            client_type = ClientType.DII
            instrument = InstrumentType.CASH
            long_value = record["DII Gross Purchase"]
            short_value = record["DII Gross Sales"]
            result_record = self.__parse_eod_record(
                date, client_type, instrument, None, long_value, short_value
            )
            result_records.append(result_record)

            break

        return result_records

    def pull_parse_eod_data(self, date):
        url_record = self.urls["fo_participant_oi"]
        url = StringHelper.format_url(url_record, date)
        self.logger.log_debug(f"Started with {url}.")

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        # pull csv containing all the listed equities from web
        data = LogicHelper.reading_csv_raw(url=url, skiprows=1)

        entities = []
        for record in data:
            result_records = self.__parse_eod_data(date, record)

            for result_record in result_records:
                entities.append(result_record)

        cash_entities = self.__parse_participant_cash(date)
        for entity in cash_entities:
            entities.append(entity)

        return entities

    def pull_parse_eod_stats(self, date):
        url_record = self.urls["fii_stats"]
        url = StringHelper.format_url(url_record, date)
        self.logger.log_debug(f"Started with {url}.")

        if self.exchange is None:
            self.logger.log_warning(f"Exchange '{self.exchange_symbol}' doesn't exists")
            return None

        data = pd.read_excel(url, header=2)
        data = data.head(4)
        data.rename(
            columns={
                "Unnamed: 0": "instrument",
                "No. of contracts": "no_of_contracts_bought",
                "Amt in Crores": "value_of_contracts_bought",
                "No. of contracts.1": "no_of_contracts_sold",
                "Amt in Crores.1": "value_of_contracts_sold",
                "No. of contracts.2": "open_interest",
                "Amt in Crores.2": "value_of_open_interest",
            },
            inplace=True,
        )  # rename

        entities = []
        for _, record in data.iterrows():
            entity = self.__parse_eod_stats_record(date, record)

            if entity is not None:
                entities.append(entity)

        return entities
