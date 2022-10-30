from ontrack.market.querysets.lookup import (
    ExchangeQuerySet,
    MarketDayCategoryQuerySet,
    MarketDayQuerySet,
    MarketDayTypeQuerySet,
)
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper


class HolidayData:
    def __init__(
        self,
        exchange_qs: ExchangeQuerySet,
        daytype_qs: MarketDayTypeQuerySet,
        category_qs: MarketDayCategoryQuerySet,
        day_qs: MarketDayQuerySet,
    ):
        self.logger = ApplicationLogger()
        self.exchange_qs = exchange_qs
        self.daytype_qs = daytype_qs
        self.category_qs = category_qs
        self.day_qs = day_qs

    def __process_record(self, daytype, category, record):
        date = dt.str_to_datetime(record["tradingDate"], "%d-%b-%Y", self.timezone)
        day = record["day"] if "day" in record else None
        is_working = record["is_working_day"] if "is_working_day" in record else False
        start_time = record["start_time"] if "start_time" in record else None
        end_time = record["end_time"] if "end_time" in record else None
        description = record["description"]

        filter = {
            "category_id": category.id,
            "daytype_id": daytype.id,
            "date": date,
            "day": day,
        }

        pk = None
        dayobj = self.day_qs.unique_search(**filter).first()
        if dayobj is not None:
            pk = dayobj.id

        entity = {}
        entity["id"] = pk
        entity["category"] = category
        entity["daytype"] = daytype
        entity["date"] = date
        entity["day"] = day
        entity["is_working_day"] = is_working
        entity["description"] = description
        entity["start_time"] = start_time
        entity["end_time"] = end_time
        entity["updated_at"] = dt.current_date_time()

        return entity

    def __process_day_type(self, exchange, daytype):
        self.timezone = exchange.time_zone.zone

        holiday_types = [
            x
            for x in self.holiday_config
            if x["exchange_symbol"] == exchange.symbol and x["type"] == daytype.name
        ]

        if not holiday_types:
            self.logger.log_info(
                f"Holiday types not exists [{exchange.symbol}] [{daytype.name}]."
            )

            return None

        self.logger.log_debug(
            f"Started with Config Holiday [{exchange.symbol}] [{daytype.name}]."
        )

        headers = Configurations.get_header_values_config()
        holiday_type = holiday_types[0]
        holidays = LogicHelper.pull_data_from_external_api(holiday_type, headers)

        entities = []
        for category in list(daytype.categories.all()):
            if category.code not in holidays:
                self.logger.log_debug("Category not enabled or exists.")
                continue

            records = holidays[category.code]
            for record in records:
                entity = self.__process_record(daytype, category, record)
                entities.append(entity)
        return entities

    def pull_parse_exchange_holidays(self):
        exchanges = self.exchange_qs.all()
        self.holiday_config = Configurations.get_urls_config()["holidays"]

        results = []
        for exchange in exchanges:
            self.logger.log_debug(f"Starting with {exchange.symbol}.")

            for datatype in list(exchange.day_types.all()):
                result = self.__process_day_type(exchange, datatype)
                if result is not None:
                    results += result

        return results
