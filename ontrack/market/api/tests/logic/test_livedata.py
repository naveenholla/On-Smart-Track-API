import pytest

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.logic.livedata import LiveData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.lookup import Equity, Exchange, Index
from ontrack.utils.base.enum import ExchangeType


class TestLogicLiveData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def equity_index_data_fixture(self, market_lookup_data_fixture: MarketLookupData):
        self.marketlookupdata = market_lookup_data_fixture
        records = self.marketlookupdata.load_equity_data()
        self.marketlookupdata.create_or_update(records, Equity)

        records = self.marketlookupdata.load_index_data()
        self.marketlookupdata.create_or_update(records, Index)

        self.settings = SettingLogic()

    @pytest.mark.unittest
    def test_execute_equity_live_data_task(self):
        obj = LiveData(ExchangeType.NSE)
        result = obj.execute_equity_live_data_task()
        assert result is not None
