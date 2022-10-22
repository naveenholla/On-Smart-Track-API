import pytest

from ontrack.market.data.holidays import HolidayData
from ontrack.market.data.initialize import InitializeData
from ontrack.market.models.lookup import (
    Exchange,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)


class TestPullHolidayData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.all()
        self.daytype_qs = MarketDayType.backend.all()
        self.category_qs = MarketDayCategory.backend.all()
        self.day_qs = MarketDay.backend.all()

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_parse_exchange_holidays(self):
        InitializeData().load_holidays_data()
        holiday_obj = HolidayData(
            self.exchange_qs, self.daytype_qs, self.category_qs, self.day_qs
        )
        holidays = holiday_obj.pull_parse_exchange_holidays()
        assert len(holidays) > 0
