from ontrack.market.querysets.lookup import ExchangeQuerySet
from ontrack.market.querysets.participant import ParticipantActivityQuerySet
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
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.participant_qs = participant_qs
        self.exchange_symbol = exchange_symbol

        self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()
        self.urls = Configurations.get_urls_config()

        self.client_type = {
            value.lower(): key.lower() for key, value in ClientType.choices
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

        return entities
