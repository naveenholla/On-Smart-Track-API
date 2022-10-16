from django.db import transaction

from ontrack.admin_lookup.models import Setting as AdminSetting
from ontrack.utils.base.enum import (
    AdminSettingKey,
    ExchangeType,
    HolidayCategoryType,
    MarketDayTypeEnum,
)
from ontrack.utils.config import Configurations
from ontrack.utils.context import (
    application_context,
    application_context_destroy,
    get_correlation_id,
)
from ontrack.utils.datetime import DateTimeHelper
from ontrack.utils.exception import Error_While_Data_Pull
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.logic import LogicHelper
from ontrack.utils.numbers import NumberHelper
from ontrack.utils.string import StringHelper

from ..models import Indice, IndiceEndOfDay


class IndicesDataPullLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def get_pull_indices_eod_data_task(self):
        date_key = AdminSettingKey.DATAPULL_INDICES_EOD_DATA_DATE
        last_pull_date = AdminSetting.datapull_manager.get_setting(date_key)

        if last_pull_date is None:
            return DateTimeHelper.convert_string_to_datetime(
                Configurations.get_default_values_config()[
                    "default_start_date_indices_data_pull"
                ]
            )

        return DateTimeHelper.convert_string_to_datetime(last_pull_date)

    def save_pull_indices_eod_data_task_time(self, date):
        date_key = AdminSettingKey.DATAPULL_INDICES_EOD_DATA_DATE
        AdminSetting.datapull_manager.save_setting(
            date_key, DateTimeHelper.convert_datetime_to_string(date)
        )

    def pull_indices_eod_data(self, urls, date):
        url_record = urls["indices_bhavcopy"]  # get the all listed indices url
        url = StringHelper.format_url(url_record, date)

        self.logger.log_debug(f"Started with {url}.")

        # fetch page source using requests.get()
        data = LogicHelper.reading_csv_pandas_web(
            url=url
        )  # pull csv containing all the listed equities from web
        data.columns = (
            data.columns.str.strip()
        )  # remove extra spaces from the column names
        StringHelper.whitespace_remover(
            data
        )  # applying whitespace_remover function on dataframe
        data.rename(
            columns={
                "Index Name": "name",
                "Open Index Value": "open_price",
                "High Index Value": "high_price",
                "Low Index Value": "low_price",
                "Closing Index Value": "close_price",
                "Points Change": "point_changed",
                "Change(%)": "percentage_changed",
                "Volume": "traded_quantity",
                "Turnover (Rs. Cr.)": "turn_overs_in_cr",
                "P/E": "index_pe",
                "P/B": "index_pb",
                "Div Yield": "index_div_yield",
                "Index Date": "date",
            },
            inplace=True,
        )  # rename the column name
        data = data[
            [
                "name",
                "open_price",
                "high_price",
                "low_price",
                "close_price",
                "point_changed",
                "percentage_changed",
                "traded_quantity",
                "turn_overs_in_cr",
                "index_pe",
                "index_pb",
                "index_div_yield",
                "date",
            ]
        ]  # select only specific columns
        self.logger.log_debug(f"{data.count}")

        return data

    @transaction.atomic
    def save_indices_eod_data(self, data, indices, date):
        records_to_create = []
        records_to_update = []
        for _, record in data.iterrows():
            indice = indices.search_unique_record(record).first()

            if indice is None:
                self.logger.log_warning(
                    f"Can't find indice with name [name='{record['name']}',date='{record['date']}']."
                )
                # indice = MarketIndicesSector(name=record['name'])
                # indice.save()
                continue

            record["date"] = DateTimeHelper.convert_string_to_datetime(
                record["date"], "%d-%m-%Y"
            )
            d = IndiceEndOfDay(
                indice=indice,
                open_price=NumberHelper.convert_string_to_float(record["open_price"]),
                high_price=NumberHelper.convert_string_to_float(record["high_price"]),
                low_price=NumberHelper.convert_string_to_float(record["low_price"]),
                close_price=NumberHelper.convert_string_to_float(record["close_price"]),
                point_changed=NumberHelper.convert_string_to_float(
                    record["point_changed"]
                ),
                percentage_changed=NumberHelper.convert_string_to_float(
                    record["percentage_changed"]
                ),
                traded_quantity=NumberHelper.convert_string_to_float(
                    record["traded_quantity"]
                ),
                turn_overs_in_cr=NumberHelper.convert_string_to_float(
                    record["turn_overs_in_cr"]
                ),
                index_pe=NumberHelper.convert_string_to_float(record["index_pe"]),
                index_pb=NumberHelper.convert_string_to_float(record["index_pb"]),
                index_div_yield=NumberHelper.convert_string_to_float(
                    record["index_div_yield"]
                ),
                date=record["date"],
                updated_at=DateTimeHelper.current_date_time(),
                created_at=DateTimeHelper.current_date_time(),
            )

            records_to_create.append(d)

        IndiceEndOfDay.datapull_manager.bulk_create_or_update(
            records_to_create,
            records_to_update,
            [
                "indice",
                "open_price",
                "high_price",
                "low_price",
                "close_price",
                "point_changed",
                "percentage_changed",
                "traded_quantity",
                "turn_overs_in_cr",
                "index_pe",
                "index_pb",
                "index_div_yield",
                "date",
                "updated_at",
            ],
        )

        self.save_pull_indices_eod_data_task_time(date)
        return f"{len(records_to_create)} records created, {len(records_to_update)} records updated."

    def pull_and_save_indices_eod_data(self):
        try:
            date = DateTimeHelper.get_future_date(
                self.get_pull_indices_eod_data_task(), days=1
            )
            urls = Configurations.get_urls_config()  # get the urls from configurations
            indices = Indice.datapull_manager.all()  # get all equities

            output = ""
            currentdate = DateTimeHelper.current_date()

            self.logger.log_debug(f"Current Date:{currentdate}")
            self.logger.log_debug(f"Date:{date}")

            IndiceEndOfDay.datapull_manager.delete_records_after_date(
                date=date
            )  # delete all the future records
            while date <= currentdate:
                self.logger.log_debug(f"Date:{date}")

                if DateTimeHelper.is_holiday(date):
                    date = DateTimeHelper.get_future_date(date, days=1)
                    self.logger.log_info(f"{date} is holiday.")
                    continue

                if not DateTimeHelper.is_data_refreshed(date):
                    date = DateTimeHelper.get_future_date(date, days=1)
                    self.logger.log_info(f"{date} is not refreshed yet.")
                    continue

                data = self.pull_indices_eod_data(urls, date)  # pull indices data
                result = self.save_indices_eod_data(data, indices, date)
                output += f"[{result}]"

                date = DateTimeHelper.get_future_date(date, days=1)

            return output

        except Exception as e:
            message = f"Request exception from pull indices data task - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e

    def execute_pull_indices_eod_data_task(self):
        try:
            output = ""
            correlationid = get_correlation_id()
            with application_context(
                correlationid=correlationid,
                exchange_name=ExchangeType.NSE,
                holiday_category_name=HolidayCategoryType.EQUITIES,
                holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAY,
            ):
                self.logger.log_info("Started execute_pull_indices_eod_data_task task.")

                result = self.pull_and_save_indices_eod_data()
                output += f"[{result}]"

                self.logger.log_info(
                    f"Completed execute_pull_indices_eod_data_task task. {output}"
                )
                application_context_destroy()
            return output

        except Exception as e:
            message = f"Request exception from execute_pull_indices_eod_data_task task - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e
