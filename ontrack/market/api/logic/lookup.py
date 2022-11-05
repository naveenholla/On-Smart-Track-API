from django.db import transaction

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
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.context import application_context
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.numbers import NumberHelper as nh


class MarketLookupData(BaseLogic):
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.settings = SettingLogic()
        self.fixtureData = FixtureData()

        exchange_qs = Exchange.backend.get_queryset()
        self.exchange = exchange_qs.unique_search(exchange_symbol).first()

        if not self.exchange:
            return

        equity_qs = Equity.backend.get_queryset()
        self.equity_dict = self.create_dict(equity_qs)

        index_qs = Index.backend.get_queryset()
        self.index_dict = self.create_dict(index_qs, "name")

        equityindex_qs = EquityIndex.backend.get_queryset()
        self.equityindex_dict = self.create_dict(equityindex_qs, "equity_index")

        self.pull_equity_obj = PullEquityData(self.exchange, self.equity_dict)
        self.pull_index_obj = PullIndexData(self.exchange, self.index_dict)
        self.pull_equity_index_obj = PullEquityIndexData(
            self.exchange, self.equity_dict, self.index_dict, self.equityindex_dict
        )

        self.daytype_qs = MarketDayType.backend.get_queryset()
        self.category_qs = MarketDayCategory.backend.get_queryset()
        self.day_qs = MarketDay.backend.get_queryset()
        self.holiday_obj = HolidayData(
            self.exchange, self.daytype_qs, self.category_qs, self.day_qs
        )

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

    def load_equity_data(self):
        return self.pull_equity_obj.pull_and_parse_lookup_data()

    def load_index_data(self):
        return self.pull_index_obj.pull_and_parse_lookup_data()

    def pull_indices_market_cap(self, record):
        return self.pull_equity_index_obj.pull_indices_market_cap(record)

    def parse_indices_market_cap(self, index_name, record):
        return self.pull_equity_index_obj.parse_indices_market_cap(index_name, record)

    def load_equity_index_data(self):
        return self.pull_equity_index_obj.pull_and_parse_market_cap()

    def load_holidays_data(self):
        return self.holiday_obj.pull_parse_exchange_holidays()

    def execute_market_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange):
            date_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE
            pause_hour_key = AdminSettingKey.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS
            cet = self.can_execute_task(date_key, pause_hour_key)
            if not cet[0]:
                message = cet[1]
                self.logger.log_info(message)
                return message

            try:
                result_equity = self.load_equity_data()
                result_index = self.load_index_data()
                result_equity_index = self.load_equity_index_data()
                with transaction.atomic():
                    records_stats = self.create_or_update(result_equity, Equity)
                    output.append(self.message_creator("Equity", records_stats))

                    records_stats = self.create_or_update(result_index, Index)
                    output.append(self.message_creator("Index", records_stats))

                    records_stats = self.create_or_update(
                        result_equity_index, EquityIndex
                    )
                    output.append(self.message_creator("Equity Index", records_stats))
            except Exception as e:
                message = f"Exception - `{format(e)}`."
                self.logger.log_critical(message=message)
                output.append(self.message_creator("Lookup Data", message))

            key = AdminSettingKey.LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED
            days_count = nh.str_to_float(self.settings.get_by_key(key))
            EquityIndex.backend.delete_old_records(days_count)

            self.settings.save_task_execution_time(date_key)

        return output

    def execute_holidays_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange):
            date_key = AdminSettingKey.DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE
            pause_hour_key = AdminSettingKey.DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS
            cet = self.can_execute_task(date_key, pause_hour_key)
            if not cet[0]:
                message = cet[1]
                self.logger.log_info(message)
                return message

            result = self.load_holidays_data()
            records_stats = self.create_or_update(result, MarketDay)
            output.append(self.message_creator("Holidays", records_stats))

            self.settings.save_task_execution_time(date_key)

        return output
