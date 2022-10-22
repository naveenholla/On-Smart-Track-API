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
    def __init__(self):
        self.logger = ApplicationLogger()
        self.commonobj = CommonData()

    def load_fixtures_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
        ]

        temp_folder = FileSystemHelper.create_temp_folder("fixtures", temp_folder_path)

        app_folder = settings.APPS_FOLDER_NAME

        for fixture in fixtures:
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

    def load_equity_data(self, exchange_symbol, save_data=True):
        exchange_qs = Exchange.backend.all()
        equity_qs = Equity.backend.all()

        pull_equity_obj = PullEquityData(
            exchange_qs,
            equity_qs,
            exchange_symbol,
        )

        result = pull_equity_obj.pull_and_parse_equity_data()
        if save_data:
            self.commonobj.create_or_update(result, Equity, Equity.backend)

        return result

    def load_index_data(self, exchange_symbol, save_data=True):
        exchange_qs = Exchange.backend.all()
        index_qs = Index.backend.all()

        pull_index_obj = PullIndexData(
            exchange_qs,
            index_qs,
            exchange_symbol,
        )
        result = pull_index_obj.pull_and_parse_indice_data()
        if save_data:
            self.commonobj.create_or_update(result, Index, Index.backend)

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
            self.commonobj.create_or_update(result, EquityIndex, EquityIndex.backend)

        return result

    def load_holidays_data(self, save_data=True):

        exchange_qs = Exchange.backend.all()
        daytype_qs = MarketDayType.backend.all()
        category_qs = MarketDayCategory.backend.all()
        day_qs = MarketDay.backend.all()

        holiday_obj = HolidayData(exchange_qs, daytype_qs, category_qs, day_qs)
        result = holiday_obj.pull_parse_exchange_holidays()
        if save_data:
            self.commonobj.create_or_update(result, MarketDay, MarketDay.backend)
        return result

    def load_initial_data(self, exchange_symbol):
        self.load_fixtures_data()
        self.load_equity_data(exchange_symbol)
        self.load_index_data(exchange_symbol)
        self.load_equity_index_data()
        self.load_holidays_data()
