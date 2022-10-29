import pytest

from ontrack.market.models.lookup import Exchange
from ontrack.utils.base.enum import HolidayCategoryType, MarketDayTypeEnum


class TestExchangeData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def exchange_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture

    @pytest.mark.unittest
    def test_exchange_holiday(self):
        daytype = MarketDayTypeEnum.TRADING_HOLIDAYS
        category = HolidayCategoryType.EQUITIES
        self.exchange_qs.unique_search()
        days = self.exchange_fixture.get_days_by_category(daytype, category)
        assert days is not None
        assert len(list(days.all())) > 0
