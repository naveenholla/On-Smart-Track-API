from functools import lru_cache

from django.db import transaction
from django.db.models import Prefetch

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
from ontrack.utils.base.enum import AdminSettingKey as sk
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

        self.exchange_symbol = exchange_symbol

    @lru_cache(1)
    def exchange(self):
        if not self.exchange_symbol:
            return

        datetype = MarketDayType.backend.all()
        days = MarketDay.backend.prefetch_related(
            Prefetch("daytype", queryset=datetype, to_attr="type")
        )
        catgories = MarketDayCategory.backend.prefetch_related(
            Prefetch("days", queryset=days, to_attr="holidays")
        )

        exchange = (
            Exchange.backend.unique_search(self.exchange_symbol)
            .prefetch_related(
                Prefetch("holiday_categories", queryset=catgories, to_attr="categories")
            )
            .first()
        )

        return exchange

    @lru_cache(1)
    def equity_dict(self):
        exchange = self.exchange()
        qs = Equity.backend.filter(exchange_id=exchange.id)
        return qs

    @lru_cache(1)
    def index_dict(self):
        exchange = self.exchange()
        qs = Index.backend.filter(exchange_id=exchange.id)
        return qs

    @lru_cache(1)
    def equityindex_dict(self):
        exchange = self.exchange()
        qs = EquityIndex.backend.filter(equity__exchange_id=exchange.id)
        return qs

    @lru_cache(1)
    def daytype_dict(self):
        qs = MarketDayType.backend.all()
        return qs

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
        pull_equity_obj = PullEquityData(self.exchange(), self.equity_dict())
        result = pull_equity_obj.pull_and_parse_lookup_data()
        self.equity_dict.cache_clear()
        return result

    def load_index_data(self):
        pull_index_obj = PullIndexData(self.exchange(), self.index_dict())
        result = pull_index_obj.pull_and_parse_lookup_data()
        self.index_dict.cache_clear()
        return result

    def pull_indices_market_cap(self, record):
        ex = self.exchange()
        eq = self.equity_dict()
        inx = self.index_dict()
        eqinx = self.equityindex_dict()
        obj = PullEquityIndexData(ex, eq, inx, eqinx)
        result = obj.pull_indices_market_cap(record)
        return result

    def parse_indices_market_cap(self, index_name, record):
        ex = self.exchange()
        eq = self.equity_dict()
        inx = self.index_dict()
        eqinx = self.equityindex_dict()
        obj = PullEquityIndexData(ex, eq, inx, eqinx)
        result = obj.parse_indices_market_cap(index_name, record)
        return result

    def load_equity_index_data(self):
        ex = self.exchange()
        eq = self.equity_dict()
        inx = self.index_dict()
        eqinx = self.equityindex_dict()
        obj = PullEquityIndexData(ex, eq, inx, eqinx)
        result = obj.pull_and_parse_market_cap()
        self.equityindex_dict.cache_clear()
        return result

    def load_holidays_data(self):
        ex = self.exchange()
        dty = self.daytype_dict()
        obj = HolidayData(ex, dty)
        return obj.pull_parse_exchange_holidays()

    def execute_market_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange()):
            date_key = sk.DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS
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

            key = sk.LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED
            days_count = nh.str_to_float(self.settings.get_by_key(key))
            EquityIndex.backend.delete_old_records(days_count)

            self.settings.save_task_execution_time(date_key)

        return output

    def execute_holidays_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange()):
            date_key = sk.DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS
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
