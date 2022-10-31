from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.holidays import HolidayData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.data.index_equity import PullEquityIndexData
from ontrack.market.models.lookup import (
    Equity,
    EquityIndex,
    Exchange,
    Index,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)
from ontrack.utils.base.enum import AdminSettingKey
from ontrack.utils.base.fixtures import FixtureData
from ontrack.utils.base.manager import CommonLogic
from ontrack.utils.config import Configurations
from ontrack.utils.context import application_context, get_correlation_id
from ontrack.utils.exception import Error_While_Data_Pull
from ontrack.utils.logger import ApplicationLogger


class InitializeData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonLogic()
        self.fixtureData = FixtureData()
        self.settings = SettingLogic()

        self.exchange_symbol = exchange_symbol

        self.exchange_qs = Exchange.backend.get_queryset()
        self.equity_qs = Equity.backend.get_queryset()
        self.index_qs = Index.backend.get_queryset()
        self.equityindex_qs = EquityIndex.backend.get_queryset()
        self.daytype_qs = MarketDayType.backend.get_queryset()
        self.category_qs = MarketDayCategory.backend.get_queryset()
        self.day_qs = MarketDay.backend.get_queryset()

    def load_fixtures_all_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
            "market.marketday",
            "market.equity",
            "market.index",
            "market.equityindex",
        ]

        self.fixtureData.load_fixtures_data(fixtures, temp_folder_path)

    def load_fixtures_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
            "market.marketday",
        ]

        self.fixtureData.load_fixtures_data(fixtures, temp_folder_path)

    def load_equity_data(self, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            self.exchange_qs,
            self.equity_qs,
        )

        result = pull_equity_obj.pull_and_parse_lookup_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(result, Equity)

        return result, records_stats

    def load_index_data(self, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            self.exchange_qs,
            self.index_qs,
        )
        result = pull_index_obj.pull_and_parse_lookup_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(result, Index)

        return result, records_stats

    def load_equity_index_data(self, save_data=True):
        pull_equity_index_obj = PullEquityIndexData(
            self.exchange_qs, self.index_qs, self.equity_qs, self.equityindex_qs
        )
        result = pull_equity_index_obj.pull_and_parse_market_cap()
        if save_data:
            records_stats = self.commonobj.create_or_update(result, EquityIndex)

        return result, records_stats

    def load_holidays_data(self, save_data=True):
        holiday_obj = HolidayData(
            self.exchange_qs, self.daytype_qs, self.category_qs, self.day_qs
        )
        result = holiday_obj.pull_parse_exchange_holidays()
        if save_data:
            records_stats = self.commonobj.create_or_update(result, MarketDay)
        return result, records_stats

    def load_initial_data(self):
        self.load_fixtures_all_data()

    def execute_equity_lookup_data_task(self):
        try:
            self.logger.log_info("Started execute equity lookup task.")

            output = ""
            correlationid = get_correlation_id()
            with application_context(
                correlationid=correlationid, exchange_name=self.exchange_symbol
            ):
                date_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_DATE
                pause_hour_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS

                if not self.settings.can_execute_task(date_key, pause_hour_key):
                    message = "Task is paused for time being."
                    self.logger.log_info(message)
                    return message

                result = self.load_equity_data()
                output += f"[Equity - {result[1][0]} created, {result[1][1]} updated.]"

                result = self.load_index_data()
                output += f"[Index - {result[1][0]} created, {result[1][1]} updated.]"

                result = self.load_equity_index_data()
                output += (
                    f"[Equity Index - {result[1][0]} created, {result[1][1]} updated.]"
                )

                days_count = Configurations.get_default_value_by_key(
                    AdminSettingKey.LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED
                )
                EquityIndex.backend.delete_old_records(days_count)

                self.settings.save_task_execution_time(date_key)

            self.logger.log_info(f"Completed. {output}")
            return output

        except Exception as e:
            message = f"Exception - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e

    def execute_holidays_lookup_data_task(self):
        try:
            self.logger.log_info("Started execute equity lookup task.")

            output = ""
            correlationid = get_correlation_id()
            with application_context(
                correlationid=correlationid, exchange_name=self.exchange_symbol
            ):
                date_key = AdminSettingKey.DATAPULL_HOLIDAYS_LOOKUP_DATE
                pause_hour_key = AdminSettingKey.DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS

                if not self.settings.can_execute_task(date_key, pause_hour_key):
                    message = "Task is paused for time being."
                    self.logger.log_info(message)
                    return message

                result = self.load_holidays_data()
                output += (
                    f"[Holidays - {result[1][0]} created, {result[1][1]} updated.]"
                )

                self.settings.save_task_execution_time(date_key)

            self.logger.log_info(f"Completed. {output}")
            return output

        except Exception as e:
            message = f"Exception - `{format(e)}`."
            self.logger.log_critical(message=message)
            raise Error_While_Data_Pull() from e
