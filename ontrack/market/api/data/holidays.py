from ontrack.market.models.lookup import Exchange, MarketDayCategory, MarketDayType
from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper


class HolidayData:
    def __init__(
        self,
        exchange: Exchange,
        daytype_dict: dict,
    ):
        self.logger = ApplicationLogger()
        self.exchange = exchange
        self.daytype_dict = daytype_dict

    def __process_record(
        self, daytype: MarketDayType, category: MarketDayCategory, record
    ):
        date = dt.str_to_datetime(record["tradingDate"], "%d-%b-%Y", self.timezone)
        day = record["day"] if "day" in record else None
        is_working = record["is_working_day"] if "is_working_day" in record else False
        start_time = record["start_time"] if "start_time" in record else None
        end_time = record["end_time"] if "end_time" in record else None
        description = record["description"]

        pk = None
        holidays = self.exchange.get_days_by_category(
            daytype.name, category.display_name
        )
        dayobj = [e for e in holidays if dt.compare_date(date, e.date) and e.day == day]
        if len(dayobj) > 0:
            pk = dayobj[0].id

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
        self.logger.log_debug(f"Starting with {self.exchange.symbol}.")

        day_type_name = type_record["type"]

        day_type = [
            e for e in self.daytype_dict if e.name.lower() == day_type_name.lower()
        ]
        if len(day_type) == 0:
            self.logger.log_info(f"Holiday types '{day_type_name}' not exists.")
            return None
        day_type = day_type[0]

        if not self.exchange.categories or len(self.exchange.categories) == 0:
            self.logger.log_info("Categories doesn't exists.")
            return None

        self.timezone = self.exchange.timezone_name

        headers = Configurations.get_header_values_config()
        holidays = LogicHelper.pull_data_from_external_api(type_record, headers)

        entities = []
        for category in list(self.exchange.categories):
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
