import pytest

from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.api.logic.livedata import LiveData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.api.tests.test_base import (
    assert_record_creation,
    assert_record_updation,
    test_date,
)
from ontrack.market.models.equity import (
    EquityDerivativeEndOfDay,
    EquityEndOfDay,
    EquityLiveData,
    EquityLiveDerivativeData,
    EquityLiveOpenInterest,
    EquityLiveOptionChain,
)
from ontrack.market.models.lookup import Equity


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.equity_qs = Equity.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def equity_data_fixture(
        self, exchange_fixture, market_lookup_data_fixture: MarketLookupData
    ):
        self.exchange_fixture = exchange_fixture
        self.marketlookupdata = market_lookup_data_fixture

        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)
        self.livedata = LiveData(exchange_fixture.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        records = self.marketlookupdata.load_equity_data()
        self.endofdaydata.create_or_update(records, Equity)
        assert len(records) > 0

        stocks_with_lot_size = [x for x in records if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 150

        stock = [x for x in records if x["symbol"] == "hdfcbank"][0]
        assert stock["lot_size"] > 0

        equity_fixture = self.equity_qs.unique_search(symbol="reliance").first()
        assert equity_fixture is not None and equity_fixture.id is not None
        symbol = equity_fixture.symbol
        stock2 = [x for x in records if x["symbol"] == symbol][0]
        assert stock2["id"] == equity_fixture.id

        # check update logic
        records = self.marketlookupdata.load_equity_data()
        record_stats = self.endofdaydata.create_or_update(records, Equity)
        assert_record_updation((records, record_stats))

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date)
        records_stats = self.endofdaydata.create_or_update(result, EquityEndOfDay)
        assert_record_creation((result, records_stats))

        # check update logic
        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date)
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_equity_derivative_eod_data(date)
        records_stats = self.endofdaydata.create_or_update(
            result, EquityDerivativeEndOfDay
        )
        assert_record_creation((result, records_stats))

        # check update logic
        date = test_date
        result = self.endofdaydata.load_equity_derivative_eod_data(date)
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_data()
        records_stats = self.livedata.create_or_update(result, EquityLiveData)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_equity_live_data()
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_open_interest_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_open_interest_data()
        records_stats = self.livedata.create_or_update(result, EquityLiveOpenInterest)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_equity_live_open_interest_data()
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_derivative_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_derivative_data()
        records_stats = self.livedata.create_or_update(result, EquityLiveDerivativeData)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_equity_live_derivative_data()
        assert len(result) == 0

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_option_chain_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_option_chain_data()
        records_stats = self.livedata.create_or_update(result, EquityLiveOptionChain)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_equity_live_option_chain_data()
        assert len(result) == 0
