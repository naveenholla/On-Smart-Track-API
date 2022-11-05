from ontrack.market.models.lookup import Exchange
from ontrack.market.querysets.lookup import (
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
        exchange: Exchange,
        daytype_qs: MarketDayTypeQuerySet,
        category_qs: MarketDayCategoryQuerySet,
        day_qs: MarketDayQuerySet,
    ):
        self.logger = ApplicationLogger()
        self.exchange = exchange
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

    def __process_day_type(self, type_record):
        exchange_symbol = type_record["exchange_symbol"]
        day_type_name = type_record["type"]

        day_type = self.daytype_qs.unique_search(day_type_name).first()

        if self.exchange is None or day_type is None:
            self.logger.log_info(
                f"Exchange '{exchange_symbol}' of Holiday types '{day_type_name}' not exists."
            )
            return None

        self.logger.log_debug(f"Starting with {self.exchange.symbol}.")
        self.timezone = self.exchange.timezone_name

        headers = Configurations.get_header_values_config()
        holidays = LogicHelper.pull_data_from_external_api(type_record, headers)

        entities = []
        for category in list(self.exchange.holiday_categories.all()):
            if category.code not in holidays:
                self.logger.log_debug("Category not enabled or exists.")
                continue

            records = holidays[category.code]
            for record in records:
                entity = self.__process_record(day_type, category, record)
                entities.append(entity)
        return entities

    def pull_parse_exchange_holidays(self):
        self.holiday_config = Configurations.get_urls_config()["holidays"]

        results = []
        for record in self.holiday_config:
            result = self.__process_day_type(record)
            if result is not None:
                results += result

        return results
