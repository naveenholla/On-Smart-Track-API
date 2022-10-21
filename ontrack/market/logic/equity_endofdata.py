from django.db import transaction
from django.db.models import Avg

from ontrack.lookup.models import Setting as AdminSetting
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

from ..models.equity import Equity, EquityEndOfDay


class EquityDataPullLogic:
    def __init__(self):
        self.logger = ApplicationLogger()

    def get_pull_equity_eod_data_task(self):
        date_key = AdminSettingKey.DATAPULL_EQUITY_EOD_DATA_DATE
        last_pull_date = AdminSetting.datapull_manager.get_setting(date_key)

        if last_pull_date is None:
            return DateTimeHelper.string_to_datetime(
                Configurations.get_default_values_config()[
                    "default_start_date_equity_data_pull"
                ]
            )

        return DateTimeHelper.string_to_datetime(last_pull_date)

    def save_pull_equity_eod_data_task_time(self, date):
        date_key = AdminSettingKey.DATAPULL_EQUITY_EOD_DATA_DATE
        AdminSetting.datapull_manager.save_setting(
            date_key, DateTimeHelper.convert_datetime_to_string(date)
        )

    def pull_equity_eod_data(self, urls, date):
        url_record = urls["equity_bhavcopy"]  # get the all listed equity url
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
        data = data[data["SERIES"] == "EQ"]
        data.rename(
            columns={
                "SYMBOL": "symbol",
                "PREV_CLOSE": "prev_close",
                "OPEN_PRICE": "open_price",
                "HIGH_PRICE": "high_price",
                "LOW_PRICE": "low_price",
                "LAST_PRICE": "last_price",
                "CLOSE_PRICE": "close_price",
                "AVG_PRICE": "avg_price",
                "TTL_TRD_QNTY": "traded_quantity",
                "TURNOVER_LACS": "turn_overs_in_lacs",
                "NO_OF_TRADES": "number_of_trades",
                "DELIV_QTY": "delivery_quantity",
                "DELIV_PER": "delivery_percentage",
                "DATE1": "date",
            },
            inplace=True,
        )  # rename the column name
        data = data[
            [
                "symbol",
                "prev_close",
                "open_price",
                "high_price",
                "low_price",
                "last_price",
                "close_price",
                "avg_price",
                "traded_quantity",
                "turn_overs_in_lacs",
                "number_of_trades",
                "delivery_quantity",
                "delivery_percentage",
                "date",
            ]
        ]  # select only specific columns
        self.logger.log_debug(f"{data.count}")

        return data

    @transaction.atomic
    def save_equity_eod_data(self, data, equities, date):
        records_to_create = []
        records_to_update = []
        for _, record in data.iterrows():
            equity = equities.unique_search(record).first()

            if equity is None:
                self.logger.log_warning(
                    f"Can't find equity with name [symbol='{record['symbol']}',date='{record['date']}']."
                )
                equity = Equity(name=record["symbol"], symbol=record["symbol"])
                equity.save()

            record["date"] = DateTimeHelper.string_to_datetime(
                record["date"], "%d-%b-%Y"
            )
            records_for_average = (
                EquityEndOfDay.datapull_manager.get_records_after_date(query=record)
            )
            average_values = records_for_average.aggregate(
                average_quantity_per_trade=Avg("quantity_per_trade"),
                average_volumn=Avg("traded_quantity"),
                average_delivery_percentage=Avg("delivery_quantity"),
                average_open_interest=Avg("open_interest"),
            )
            d = EquityEndOfDay(
                equity=equity,
                prev_close=NumberHelper.str_to_float(record["prev_close"]),
                open_price=NumberHelper.str_to_float(record["open_price"]),
                high_price=NumberHelper.str_to_float(record["high_price"]),
                low_price=NumberHelper.str_to_float(record["low_price"]),
                last_price=NumberHelper.str_to_float(record["last_price"]),
                close_price=NumberHelper.str_to_float(record["close_price"]),
                avg_price=NumberHelper.str_to_float(record["avg_price"]),
                traded_quantity=NumberHelper.str_to_float(record["traded_quantity"]),
                turn_overs_in_lacs=NumberHelper.str_to_float(
                    record["turn_overs_in_lacs"]
                ),
                number_of_trades=NumberHelper.str_to_float(record["number_of_trades"]),
                delivery_quantity=NumberHelper.str_to_float(
                    record["delivery_quantity"]
                ),
                delivery_percentage=NumberHelper.str_to_float(
                    record["delivery_percentage"]
                ),
                date=record["date"],
                updated_at=DateTimeHelper.current_date_time(),
                created_at=DateTimeHelper.current_date_time(),
            )

            d.point_changed = d.close_price - d.prev_close
            d.percentage_changed = d.point_changed / d.last_price * 100
            d.quantity_per_trade = d.traded_quantity / d.number_of_trades

            d.open_interest = 0
            d.promotor_holding_percentage = 0

            d.average_quantity_per_trade = average_values["average_quantity_per_trade"]
            d.average_volumn = average_values["average_volumn"]
            d.average_delivery_percentage = average_values[
                "average_delivery_percentage"
            ]
            d.average_open_interest = average_values["average_open_interest"]

            records_to_create.append(d)

        EquityEndOfDay.datapull_manager.bulk_create_or_update(
            records_to_create,
            records_to_update,
            [
                "equity",
                "prev_close",
                "open_price",
                "high_price",
                "low_price",
                "last_price",
                "close_price",
                "avg_price",
                "traded_quantity",
                "turn_overs_in_lacs",
                "number_of_trades",
                "delivery_quantity",
                "delivery_percentage",
                "date",
                "updated_at",
            ],
        )

        self.save_pull_equity_eod_data_task_time(date)
        return f"{len(records_to_create)} records created, {len(records_to_update)} records updated."

    def pull_and_save_equity_eod_data(self):
        try:
            date = DateTimeHelper.get_future_date(
                self.get_pull_equity_eod_data_task(), days=1
            )
            urls = Configurations.get_urls_config()  # get the urls from configurations
            equities = Equity.datapull_manager.all()  # get all equities

            output = ""
            currentdate = DateTimeHelper.current_date()

            self.logger.log_debug(f"Current Date:{currentdate}")
            self.logger.log_debug(f"Date:{date}")

            EquityEndOfDay.datapull_manager.delete_records_after_date(
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

                data = self.pull_equity_eod_data(urls, date)  # pull equity data
                result = self.save_equity_eod_data(data, equities, date)
                output += f"[{result}]"

                date = DateTimeHelper.get_future_date(date, days=1)

            return output

        except Exception as e:
            message = f"Request exception from pull indices data task - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e

    def execute_pull_equity_eod_data_task(self):
        try:
            output = ""
            correlationid = get_correlation_id()
            with application_context(
                correlationid=correlationid,
                exchange_name=ExchangeType.NSE,
                holiday_category_name=HolidayCategoryType.EQUITIES,
                holiday_day_type=MarketDayTypeEnum.TRADING_HOLIDAYS,
            ):
                self.logger.log_info("Started pull_equity_eod_data task.")

                result = self.pull_and_save_equity_eod_data()
                output += f"[{result}]"

                self.logger.log_info(f"Completed pull_equity_eod_data task. {output}")
                application_context_destroy()
            return output

        except Exception as e:
            message = (
                f"Request exception from pull_equity_eod_data task - `{format(e)}`."
            )
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e
