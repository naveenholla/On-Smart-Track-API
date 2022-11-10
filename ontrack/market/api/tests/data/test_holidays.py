import pytest

from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.api.tests.test_base import assert_record_updation
from ontrack.market.models.lookup import (
    Exchange,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)


class TestPullHolidayData:
    @pytest.fixture(autouse=True)
    def injector(self, market_lookup_data_fixture: MarketLookupData):
        self.exchange_qs = Exchange.backend.get_queryset()
        self.daytype_qs = MarketDayType.backend.get_queryset()
        self.category_qs = MarketDayCategory.backend.get_queryset()
        self.day_qs = MarketDay.backend.get_queryset()

        self.marketlookupdata = market_lookup_data_fixture

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_parse_exchange_holidays(self):
        result = self.marketlookupdata.load_holidays_data()
        self.marketlookupdata.create_or_update(result, MarketDay)
        assert len(result) > 0

        # check update logic
        records = self.marketlookupdata.load_holidays_data()
        record_stats = self.marketlookupdata.create_or_update(records, MarketDay)
        assert_record_updation((records, record_stats))
