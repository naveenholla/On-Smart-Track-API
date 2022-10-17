import json
from functools import lru_cache

import pandas as pd
from django.conf import settings

from ontrack.utils.base.enum import HolidayCategoryType, MarketDayTypeEnum
from ontrack.utils.logger import ApplicationLogger


class Configurations:
    logger = ApplicationLogger()

    @staticmethod
    def __get_config(fileName: str):
        path = f"{str(settings.CONFIG_DIR)}/{fileName}.json"
        Configurations.logger.log_debug(f"Reading configuration [{path}].")

        # read all the file content
        with open(path) as config:
            jsonServerData = json.load(config)
            return jsonServerData

    @staticmethod
    def __set_config(fileName: str, content):
        df = pd.DataFrame(content)
        path = f"{str(settings.CONFIG_DIR)}/{fileName}.json"

        Configurations.logger.log_debug(f"Saving configuration [{path}].")
        df.to_json(path, orient="records", compression="infer", index="true")

    @staticmethod
    def clear_cache():
        Configurations.get_urls_config.cache_clear()
        Configurations.get_default_values_config.cache_clear()
        Configurations.get_all_exchanges.cache_clear()
        Configurations.get_exchange.cache_clear()
        Configurations.get_exchange_days_by_type.cache_clear()

    @staticmethod
    @lru_cache(1)
    def get_urls_config():
        return Configurations.__get_config("urlconfig")

    @staticmethod
    @lru_cache(1)
    def get_default_values_config():
        return Configurations.__get_config("default_values")

    @staticmethod
    @lru_cache(1)
    def get_all_exchanges():
        return Configurations.__get_config("exchanges")

    @staticmethod
    def save_exchanges(content):
        Configurations.get_all_exchanges.cache_clear()
        Configurations.get_exchange.cache_clear()
        Configurations.__set_config("exchanges", content)

    @staticmethod
    @lru_cache(maxsize=5, typed=False)
    def get_exchange(exchange_name):
        exchanges = Configurations.get_all_exchanges()
        output_dictionary = [x for x in exchanges if x["name"] == str(exchange_name)]
        return output_dictionary[0]

    @staticmethod
    @lru_cache(maxsize=200, typed=False)
    def get_exchange_days_by_type(exchange_name, day_type_name, category_name):
        exchange = Configurations.get_exchange(exchange_name)
        if not exchange:
            Configurations.logger.log_warning(
                f"Exchange [{exchange_name}] doesn't exists."
            )
            return None

        day_types = exchange["day_types"]

        if not day_types or len(day_types) == 0:
            Configurations.logger.log_info(
                f"Exchange [{exchange_name}] doesn't have days types."
            )
            return None

        day_type = [x for x in day_types if x["name"] == day_type_name]

        if day_type is None or len(day_type) == 0:
            Configurations.logger.log_info(
                f"Exchange [{exchange_name}], day type [{day_type_name}] doesn't exists."
            )
            return None

        categories = day_type[0]["categories"]
        if not categories or len(categories) == 0:
            Configurations.logger.log_info(
                f"Exchange [{exchange_name}], day type [{day_type_name}] doesn't have categories."
            )
            return None

        category = [x for x in categories if x["display_name"] == category_name]

        if category is None or len(category) == 0:
            Configurations.logger.log_info(
                f"Exchange [{exchange_name}], day type [{day_type_name}],"
                " category [{category_name}] doesn't exists."
            )
            return None

        days = category[0]["days"]

        if days is None or len(days) == 0:
            Configurations.logger.log_info(
                f"Exchange [{exchange_name}], day type [{day_type_name}],"
                " category [{category_name}] doesn't have days."
            )
            return None

        Configurations.logger.log_debug(
            f"Found {len(days)} days for Exchange [{exchange_name}],"
            " day type [{day_type_name}], category [{category_name}]."
        )
        return days

    @staticmethod
    def get_exchange_weekly_off(exchange_name):
        day_type_name = MarketDayTypeEnum.WEEKLY_OFF_DAYS
        category_name = HolidayCategoryType.WEEKEND

        return Configurations.get_exchange_days_by_type(
            exchange_name, day_type_name, category_name
        )

    @staticmethod
    def get_exchange_special_days(exchange_name):
        day_type_name = MarketDayTypeEnum.SPECIAL_TRADING_DAY
        category_name = HolidayCategoryType.SPECIAL_TRADING_HOURS

        return Configurations.get_exchange_days_by_type(
            exchange_name, day_type_name, category_name
        )

    @staticmethod
    def get_exchange_trading_holidays(exchange_name, category_name):
        day_type_name = MarketDayTypeEnum.TRADING_HOLIDAY

        return Configurations.get_exchange_days_by_type(
            exchange_name, day_type_name, category_name
        )

    @staticmethod
    def get_exchange_clearing_holidays(exchange_name, category_name):
        day_type_name = MarketDayTypeEnum.CLEARING_HOLIDAY

        return Configurations.get_exchange_days_by_type(
            exchange_name, day_type_name, category_name
        )
