import pytest

from ontrack.market.api.data.holidays import HolidayData
from ontrack.market.api.logic.initialize import InitializeData
from ontrack.market.models.lookup import (
    Exchange,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)


class TestPullHolidayData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture):
        self.exchange_qs = Exchange.backend.get_queryset()
        self.daytype_qs = MarketDayType.backend.get_queryset()
        self.category_qs = MarketDayCategory.backend.get_queryset()
        self.day_qs = MarketDay.backend.get_queryset()

        self.initializeData = InitializeData(exchange_fixture.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_parse_exchange_holidays(self):
        self.initializeData.load_holidays_data()
        holiday_obj = HolidayData(
            self.exchange_qs, self.daytype_qs, self.category_qs, self.day_qs
        )
        holidays = holiday_obj.pull_parse_exchange_holidays()
        assert len(holidays) > 0
