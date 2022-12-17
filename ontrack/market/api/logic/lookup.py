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
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.context import application_context
from ontrack.utils.numbers import NumberHelper as nh


class MarketLookupData(BaseLogic):
    def __init__(self, exchange_symbol, recorder=None):
        self.settings = SettingLogic()
        self.fixtureData = FixtureData()

        self.exchange_symbol = exchange_symbol
        self.tp = TaskProgressStatus(recorder)

        self.refresh_cache()

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
        if not exchange:
            return None

        qs = Equity.backend.filter(exchange_id=exchange.id)
        return qs

    @lru_cache(1)
    def index_dict(self):
        exchange = self.exchange()
        if not exchange:
            return None

        qs = Index.backend.filter(exchange_id=exchange.id)
        return qs

    @lru_cache(1)
    def equityindex_dict(self):
        exchange = self.exchange()
        if not exchange:
            return None

        qs = EquityIndex.backend.filter(equity__exchange_id=exchange.id)
        return qs

    @lru_cache(1)
    def daytype_dict(self):
        qs = MarketDayType.backend.all()
        return qs

    def refresh_cache(self):
        ex = self.exchange()
        if not ex:
            return

        eq = self.equity_dict()
        inx = self.index_dict()
        eqinx = self.equityindex_dict()
        dty = self.daytype_dict()

        self.pull_equity_obj = PullEquityData(ex, eq, self.tp)
        self.pull_index_obj = PullIndexData(ex, inx, self.tp)
        self.pull_eqinx_obj = PullEquityIndexData(ex, eq, inx, eqinx, self.tp)
        self.pull_holidays = HolidayData(ex, dty, self.tp)

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

    def load_equity_data(self):
        result = self.pull_equity_obj.pull_and_parse_lookup_data()
        self.equity_dict.cache_clear()
        self.refresh_cache()
        self.tp.log_message("Equity Pull Completed.", "Equity Data")
        return result

    def load_index_data(self):
        result = self.pull_index_obj.pull_and_parse_lookup_data()
        self.index_dict.cache_clear()
        self.refresh_cache()
        self.tp.log_message("Index Pull Completed.", "Index Data")
        return result

    def load_equity_index_data(self):
        result = self.pull_eqinx_obj.pull_and_parse_market_cap()
        self.equityindex_dict.cache_clear()
        self.refresh_cache()
        self.tp.log_message("Equity Index Pull Completed.", "Equity Index Data")
        return result

    def pull_indices_market_cap(self, record):
        result = self.pull_eqinx_obj.pull_indices_market_cap(record)
        return result

    def parse_indices_market_cap(self, index_name, record):
        result = self.pull_eqinx_obj.parse_indices_market_cap(index_name, record)
        return result

    def load_holidays_data(self):
        return self.pull_holidays.pull_parse_exchange_holidays()

    def __save_market_lookup(self, result, modeltype, title):
        records_stats = self.create_or_update(result, modeltype)
        stats = self.message_creator(title, records_stats)
        self.output.append(stats)
        self.tp.log_records_stats(stats, f"{title} - Stats")

    def execute_market_lookup_data_task(self):
        self.output = []
        with application_context(exchange=self.exchange()):
            date_key = sk.DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS
            cet = self.can_execute_task(date_key, pause_hour_key)
            if not cet[0]:
                message = cet[1]
                self.tp.log_warning(message, is_completed=True)
                return message

            try:
                re = self.load_equity_data()
                ri = self.load_index_data()
                rei = self.load_equity_index_data()

                with transaction.atomic():
                    self.__save_market_lookup(re, Equity, "Equity")
                    self.__save_market_lookup(ri, Index, "Index")
                    self.__save_market_lookup(rei, EquityIndex, "Equity Index")
            except Exception as e:
                message = f"Exception - `{format(e)}`."
                self.tp.log_error(message)
                self.tp.log_critical(message=message)
                self.output.append(self.message_creator("Lookup Data", message))
                raise

            key = sk.LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED
            days_count = nh.str_to_float(self.settings.get_by_key(key))
            records = EquityIndex.backend.delete_old_records(days_count)
            self.tp.log_records_stats({"deleted": records}, "EquityIndex")
            self.settings.save_task_execution_time(date_key)
            self.tp.log_completed("Task Completed.")

        return self.output

    def execute_holidays_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange()):
            date_key = sk.DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS
            cet = self.can_execute_task(date_key, pause_hour_key)
            if not cet[0]:
                message = cet[1]
                self.tp.log_warning(message, is_completed=True)
                return message

            result = self.load_holidays_data()
            self.tp.log_message("Holiday Pull Completed.", "Holidays Data")

            records_stats = self.create_or_update(result, MarketDay)
            stats = self.message_creator("Holidays", records_stats)
            output.append(stats)
            self.tp.log_records_stats(stats)

            self.settings.save_task_execution_time(date_key)
            self.tp.log_completed("Task Completed.")

        return output
