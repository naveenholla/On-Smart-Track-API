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
from ontrack.utils.base.fixtures import FixtureData
from ontrack.utils.base.manager import CommonLogic
from ontrack.utils.logger import ApplicationLogger


class InitializeData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonLogic()
        self.fixtureData = FixtureData()
        self.exchange_symbol = exchange_symbol

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
        exchange_qs = Exchange.backend.get_queryset()
        equity_qs = Equity.backend.get_queryset()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
        )

        result = pull_equity_obj.pull_and_parse_lookup_data()
        if save_data:
            self.commonobj.create_or_update(result, Equity)

        return result

    def load_index_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        index_qs = Index.backend.get_queryset()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
        )
        result = pull_index_obj.pull_and_parse_lookup_data()
        if save_data:
            self.commonobj.create_or_update(result, Index)

        return result

    def load_equity_index_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        equity_qs = Equity.backend.get_queryset()
        index_qs = Index.backend.get_queryset()
        equityindex_qs = EquityIndex.backend.get_queryset()

        pull_equity_index_obj = PullEquityIndexData(
            exchange_qs, index_qs, equity_qs, equityindex_qs
        )
        result = pull_equity_index_obj.pull_and_parse_market_cap()
        if save_data:
            self.commonobj.create_or_update(result, EquityIndex)

        return result

    def load_holidays_data(self, save_data=True):

        exchange_qs = Exchange.backend.get_queryset()
        daytype_qs = MarketDayType.backend.get_queryset()
        category_qs = MarketDayCategory.backend.get_queryset()
        day_qs = MarketDay.backend.get_queryset()

        holiday_obj = HolidayData(exchange_qs, daytype_qs, category_qs, day_qs)
        result = holiday_obj.pull_parse_exchange_holidays()
        if save_data:
            self.commonobj.create_or_update(result, MarketDay)
        return result

    def load_initial_data(self):
        self.load_fixtures_all_data()
        self.load_equity_data()
        self.load_index_data()
        self.load_equity_index_data()
        self.load_holidays_data()
