from django.conf import settings
from django.core.management import call_command

from ontrack.market.data.common import CommonData
from ontrack.market.data.equity import PullEquityData
from ontrack.market.data.holidays import HolidayData
from ontrack.market.data.index import PullIndexData
from ontrack.market.data.index_equity import PullEquityIndexData
from ontrack.market.models.lookup import (
    Equity,
    EquityIndex,
    Exchange,
    Index,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)
from ontrack.utils.filesystem import FileSystemHelper
from ontrack.utils.logger import ApplicationLogger


class InitializeData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonData()
        self.exchange_symbol = exchange_symbol

    def load_fixture_data(self, fixture, temp_folder_path=None):
        temp_folder = FileSystemHelper.create_temp_folder("fixtures", temp_folder_path)
        app_folder = settings.APPS_FOLDER_NAME

        fixture_details = fixture.split(".")
        app_name = fixture_details[0]
        model = fixture_details[1]
        source = f"{app_folder}/{app_name}/fixtures/{model}.json"
        destination = temp_folder / f"{model}.json"
        print(source)
        print(destination)

        with open(source, "rb") as f:
            data = f.read()

        with open(destination, "wb") as f_new:
            f_new.write(data)

        call_command("loaddata", destination)

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

        for fixture in fixtures:
            self.load_fixture_data(fixture, temp_folder_path)

    def load_fixtures_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
        ]

        for fixture in fixtures:
            self.load_fixture_data(fixture, temp_folder_path)

    def load_equity_data(self, save_data=True):
        exchange_qs = Exchange.backend.all()
        equity_qs = Equity.backend.all()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
        )

        result = pull_equity_obj.pull_and_parse_equity_data()
        if save_data:
            self.commonobj.create_or_update(result, Equity)

        return result

    def load_index_data(self, save_data=True):
        exchange_qs = Exchange.backend.all()
        index_qs = Index.backend.all()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
        )
        result = pull_index_obj.pull_and_parse_index_data()
        if save_data:
            self.commonobj.create_or_update(result, Index)

        return result

    def load_equity_index_data(self, save_data=True):
        exchange_qs = Exchange.backend.all()
        equity_qs = Equity.backend.all()
        index_qs = Index.backend.all()
        equityindex_qs = EquityIndex.backend.all()

        pull_equity_index_obj = PullEquityIndexData(
            exchange_qs, index_qs, equity_qs, equityindex_qs
        )
        result = pull_equity_index_obj.pull_and_parse_market_cap()
        if save_data:
            self.commonobj.create_or_update(result, EquityIndex)

        return result

    def load_holidays_data(self, save_data=True):

        exchange_qs = Exchange.backend.all()
        daytype_qs = MarketDayType.backend.all()
        category_qs = MarketDayCategory.backend.all()
        day_qs = MarketDay.backend.all()

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
