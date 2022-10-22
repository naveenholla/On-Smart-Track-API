import pytz
import requests

from ontrack.utils.config import Configurations
from ontrack.utils.context import (
    application_context,
    application_context_destroy,
    get_correlation_id,
)
from ontrack.utils.datetime import DateTimeHelper
from ontrack.utils.exception import Error_While_Data_Pull
from ontrack.utils.logger import ApplicationLogger

from ..models.lookup import Exchange, MarketDay, MarketDayCategory, MarketDayType


class InitialDataPullLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def save_intial_market_exchange_data(self):
        exchanges = Configurations.get_all_exchanges()
        holiday_config = Configurations.get_urls_config()["holidays"]

        for exchange in exchanges:
            exchange_id = exchange["id"]
            exchange_name = exchange["name"]
            exchange_start_time = exchange["start_time"]
            exchange_end_time = exchange["end_time"]
            exchange_data_refresh_time = exchange["data_refresh_time"]
            exchange_time_zone = exchange["time_zone"]["zone"]

            self.logger.log_debug(f"Starting with {exchange_name}.")

            exchange_obj = Exchange.backend.filter(name=exchange_name).first()

            if not exchange_obj:
                self.logger.log_info("Exchange not exists. Creating.")
                # ALTER SEQUENCE admin_lookup_marketbroker_id_seq RESTART WITH 1
                exchange_obj = Exchange(
                    id=exchange_id,
                    name=exchange_name,
                    start_time=exchange_start_time,
                    end_time=exchange_end_time,
                    data_refresh_time=exchange_data_refresh_time,
                    time_zone=pytz.timezone(exchange_time_zone),
                )
                exchange_obj.save()

            for day_type in exchange["day_types"]:
                day_type_name = day_type["name"]
                day_type_categories = day_type["categories"]

                self.logger.log_debug("-------------------------------")
                self.logger.log_debug(f"Starting with {day_type_name} day type.")
                self.logger.log_debug("-------------------------------")

                day_type_obj = MarketDayType.objects.filter(
                    exchange__id=exchange_id, name=day_type_name
                ).first()

                if not day_type_obj:
                    self.logger.log_info("Day Type not exists. Creating.")
                    day_type_obj = MarketDayType(
                        name=day_type_name, exchange=exchange_obj
                    )
                    day_type_obj.save()

                self.logger.log_debug(
                    f"Day Type category count - {len(day_type_categories)}."
                )
                for category in day_type_categories:
                    category_code = category["code"]
                    category_parent_name = category["parent_name"]
                    category_display_name = category["display_name"]
                    category_days = category["days"]
                    category_obj = MarketDayCategory.objects.filter(
                        day_type__id=day_type_obj.id, code=category_code
                    ).first()

                    self.logger.log_debug(
                        f"Started with Category [{category_display_name}]."
                    )
                    if not category_obj:
                        self.logger.log_info("Category not exists. Creating.")
                        category_obj = MarketDayCategory(
                            day_type=day_type_obj,
                            parent_name=category_parent_name,
                            display_name=category_display_name,
                            code=category_code,
                        )
                        category_obj.save()

                    for category_day in category_days:
                        category_day_date = category_day["date"]
                        category_day_day = category_day["day"]
                        category_day_is_working_day = category_day["is_working_day"]
                        category_day_description = category_day["description"]
                        category_day_start_time = category_day["start_time"]
                        category_day_end_time = category_day["end_time"]

                        category_day_obj = MarketDay.objects.filter(
                            category__id=category_obj.id,
                            date=category_day_date,
                            day=category_day_day,
                        ).first()

                        self.logger.log_debug(
                            f"Started with Category Date [{category_day_date}], Day [[{category_day_day}]]."
                        )
                        if not category_day_obj:
                            self.logger.log_info("Category day not exists. Creating.")
                            category_day_obj = MarketDay(
                                category=category_obj,
                                date=category_day_date,
                                day=category_day_day,
                                is_working_day=category_day_is_working_day,
                                description=category_day_description,
                                start_time=category_day_start_time,
                                end_time=category_day_end_time,
                            )
                            category_day_obj.save()

                holiday_types = [
                    x
                    for x in holiday_config
                    if x["exchange"] == exchange_name and x["type"] == day_type_name
                ]
                # market_days_type_enum = {
                #     value: key for key, value in MarketDayTypeEnum.choices
                # }
                if not holiday_types:
                    self.logger.log_info(
                        f"Holiday types not exists [{exchange_name}] [{day_type_name}]."
                    )
                    continue

                self.logger.log_debug(
                    f"Started with Config Holiday [{exchange_name}] [{day_type_name}]."
                )
                for holiday_type in holiday_types:
                    url = holiday_type["url"]
                    day_type_categories = holiday_type["categories"]
                    headers = {
                        "accept-encoding": "gzip, deflate, br",
                        "accept-language": "en-US,en;q=0.9",
                        "user-agent": (
                            "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/106.0.0.0 Safari/537.36"
                        ),
                    }

                    self.logger.log_debug(f"Started with [{url}].")

                    session = requests.Session()
                    holiday_data_all = session.get(url, headers=headers).json()

                    self.logger.log_debug("Got the Data.")

                    for category in day_type_categories:
                        category_parent_name = category["parent_name"]
                        category_display_name = category["display_name"]
                        category_code = category["code"]
                        category_enabled = category["enabled"]

                        self.logger.log_debug(
                            f"Started with Category [{category_display_name}]."
                        )
                        if (
                            not category_enabled
                            or category_code not in holiday_data_all
                        ):
                            self.logger.log_debug("Category not enabled or exists.")
                            continue

                        category_obj = MarketDayCategory.objects.filter(
                            day_type__id=day_type_obj.id, code=category_code
                        ).first()
                        if not category_obj:
                            self.logger.log_info("Category not exists. Creating.")
                            category_obj = MarketDayCategory(
                                day_type=day_type_obj,
                                parent_name=category_parent_name,
                                display_name=category_display_name,
                                code=category_code,
                            )
                            category_obj.save()

                        category_days = holiday_data_all[category_code]
                        for category_day in category_days:
                            category_day_date = DateTimeHelper.string_to_datetime(
                                category_day["tradingDate"], "%d-%b-%Y"
                            )
                            category_day_day = None
                            category_day_is_working_day = False
                            category_day_description = category_day["description"]
                            category_day_start_time = None
                            category_day_end_time = None

                            self.logger.log_debug(
                                f"Started with Category Date [{category_day_date}], Day [[{category_day_day}]]."
                            )

                            category_day_obj = MarketDay.objects.filter(
                                category__id=category_obj.id,
                                date=category_day_date,
                                day=category_day_day,
                            ).first()
                            if not category_day_obj:
                                self.logger.log_info(
                                    "Category day not exists. Creating."
                                )
                                category_day_obj = MarketDay(
                                    category=category_obj,
                                    date=category_day_date,
                                    day=category_day_day,
                                    is_working_day=category_day_is_working_day,
                                    description=category_day_description,
                                    start_time=category_day_start_time,
                                    end_time=category_day_end_time,
                                )
                                category_day_obj.save()

    def execute_intial_market_lookup_data_task(self):
        try:
            correlationid = get_correlation_id()
            with application_context(correlationid=correlationid):
                self.logger.log_info(
                    "Started execute_intial_market_lookup_data_task task."
                )

                self.save_intial_market_exchange_data()

                self.logger.log_info(
                    "Completed execute_intial_market_lookup_data_task task."
                )
                application_context_destroy()
            return "Done"
        except Exception as e:
            message = f"Request exception from execute_intial_market_lookup_data_task task - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e
