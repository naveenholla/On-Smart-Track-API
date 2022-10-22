# import pytz
# import requests

# from ontrack.utils.config import Configurations
# from ontrack.utils.context import (
#     application_context,
#     application_context_destroy,
#     get_correlation_id,
# )
# from ontrack.utils.datetime import DateTimeHelper
# from ontrack.utils.exception import Error_While_Data_Pull
# from ontrack.utils.logger import ApplicationLogger

# from ..models.lookup import Exchange, MarketDay, MarketDayCategory, MarketDayType


# class HolidayData:
#     def __init__(
#         self,
#         daytype_qs: MarketDayTypeQ,
#         category_qs: MarketDayCategory,
#         day_qs: MarketDay,
#         equity_listing_url: str,
#         market_cap_url: str,
#         exchange_symbol: str,
#     ):
#         self.logger = ApplicationLogger()
#         self.exchange_qs = exchange_qs
#         self.equity_qs = equity_qs
#         self.equity_listing_url = equity_listing_url
#         self.exchange_symbol = exchange_symbol

#         self.exchange = self.exchange_qs.unique_search(self.exchange_symbol).first()
#         commonobj = CommonData()
#         self.market_cap_records = commonobj.pull_marketlot_data(market_cap_url)

#     def __process_record(self, daytype, category, record, days):
#         date  = DateTimeHelper.string_to_datetime(record["tradingDate"], "%d-%b-%Y")
#         day = record["day"] if "day" in record else None
#         is_working = record["is_working_day"] if "is_working_day" in record else False,
#         start_time = record["start_time"] if "start_time" in record else None
#         end_time = record["end_time"] if "end_time" in record else None

#         pk = None
#         dayobj = [x for x in days if x["date"] == date or x["day"] == day]
#         if dayobj is None:
#             pk = dayobj.id

#         entity = {}
#         entity["id"] = pk
#         entity["category"] = category
#         entity["date"] = date
#         entity["day"] = day
#         entity["is_working_day"] = is_working
#         entity["description"] = record["description"]
#         entity["start_time"] = start_time
#         entity["end_time"] = end_time

#         return entity

#     def __pull_holiday_data(self, url):
#         headers = {
#             "accept-encoding": "gzip, deflate, br",
#             "accept-language": "en-US,en;q=0.9",
#             "user-agent": (
#                 "Mozilla/5.0 (Windows NT 10.0; WOW64) "
#                 "AppleWebKit/537.36 (KHTML, like Gecko) "
#                 "Chrome/106.0.0.0 Safari/537.36"
#             ),
#         }

#         self.logger.log_debug(f"Started with [{url}].")
#         session = requests.Session()
#         data = session.get(url, headers=headers).json()
#         self.logger.log_debug("Got the Data.")

#         return data

#     def save_intial_market_exchange_data(self):
#         exchanges = self.exchange_qs.all()
#         holiday_config = Configurations.get_urls_config()["holidays"]

#         for exchange in exchanges:
#             self.logger.log_debug(f"Starting with {exchange_name}.")

#             for daytype in exchange.day_types:
#                 holiday_types = [
#                     x
#                     for x in holiday_config
#                     if x["exchange_symbol"] == exchange.symbol and x["type"] == daytype.name
#                 ]

#                 if not holiday_types:
#                     self.logger.log_info(
#                         f"Holiday types not exists [{exchange.symbol}] [{daytype.name}]."
#                     )
#                     continue

#                 self.logger.log_debug(
#                     f"Started with Config Holiday [{exchange.symbol}] [{day_type_name}]."
#                 )

#                 holiday_type = holiday_types[0]
#                 url = holiday_type["url"]
#                 holidays = self.__pull_holiday_data(url)

#                 for category in daytype.categories:

#                     category_days = holiday_data_all[category_code]
#                     for category_day in category_days:
#                         category_day_date = (
#                             DateTimeHelper.string_to_datetime(
#                                 category_day["tradingDate"], "%d-%b-%Y"
#                             )
#                         )
#                         category_day_day = None
#                         category_day_is_working_day = False
#                         category_day_description = category_day["description"]
#                         category_day_start_time = None
#                         category_day_end_time = None

#                         self.logger.log_debug(
#                             f"Started with Category Date [{category_day_date}], Day [[{category_day_day}]]."
#                         )

#                         category_day_obj = MarketDay.objects.filter(
#                             category__id=category_obj.id,
#                             date=category_day_date,
#                             day=category_day_day,
#                         ).first()
#                         if not category_day_obj:
#                             self.logger.log_info(
#                                 "Category day not exists. Creating."
#                             )
#                             category_day_obj = MarketDay(
#                                 category=category_obj,
#                                 date=category_day_date,
#                                 day=category_day_day,
#                                 is_working_day=category_day_is_working_day,
#                                 description=category_day_description,
#                                 start_time=category_day_start_time,
#                                 end_time=category_day_end_time,
#                             )
#                             category_day_obj.save()

#     def execute_intial_market_lookup_data_task(self):
#         try:
#             correlationid = get_correlation_id()
#             with application_context(correlationid=correlationid):
#                 self.logger.log_info(
#                     "Started execute_intial_market_lookup_data_task task."
#                 )

#                 self.save_intial_market_exchange_data()

#                 self.logger.log_info(
#                     "Completed execute_intial_market_lookup_data_task task."
#                 )
#                 application_context_destroy()
#             return "Done"
#         except Exception as e:
#             message = f"Request exception from execute_intial_market_lookup_data_task task - `{format(e)}`."
#             self.logger.log_critical(message=message)
#             raise Error_While_Data_Pull() from e
