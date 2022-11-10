import pytest

from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.api.logic.livedata import LiveData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.api.tests.test_base import (
    assert_record_creation,
    assert_record_updation,
    test_date,
)
from ontrack.market.models.index import (
    IndexDerivativeEndOfDay,
    IndexEndOfDay,
    IndexLiveData,
    IndexLiveDerivativeData,
    IndexLiveOpenInterest,
    IndexLiveOptionChain,
)
from ontrack.market.models.lookup import Index


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.index_qs = Index.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def index_data_fixture(self, market_lookup_data_fixture: MarketLookupData):
        self.marketlookupdata = market_lookup_data_fixture
        self.exchange = self.marketlookupdata.exchange()

        self.endofdaydata = EndOfDayData(self.exchange.symbol)
        self.livedata = LiveData(self.exchange.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        records = self.marketlookupdata.load_index_data()
        self.endofdaydata.create_or_update(records, Index)
        assert len(records) > 0

        stocks_with_lot_size = [x for x in records if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 2

        stock = [x for x in records if x["symbol"] == "nifty"][0]
        assert stock["lot_size"] > 0

        stock = [x for x in records if x["symbol"] == "cnxauto"][0]
        assert stock["is_sectoral"]

        index_fixture = self.index_qs.unique_search(symbol="banknifty").first()
        assert index_fixture is not None and index_fixture.id is not None
        symbol = index_fixture.symbol
        stock2 = [x for x in records if x["symbol"] == symbol][0]
        assert stock2["id"] == index_fixture.id

        # check update logic
        records = self.marketlookupdata.load_index_data()
        record_stats = self.endofdaydata.create_or_update(records, Index)
        assert_record_updation((records, record_stats))

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        date = test_date
        result = self.endofdaydata.load_index_eod_data(date)
        records_stats = self.endofdaydata.create_or_update(result, IndexEndOfDay)
        assert_record_creation((result, records_stats))

        # check update logic
        date = test_date
        result = self.endofdaydata.load_index_eod_data(date)
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        date = test_date
        result = self.endofdaydata.load_index_derivative_eod_data(date)
        records_stats = self.endofdaydata.create_or_update(
            result, IndexDerivativeEndOfDay
        )
        assert_record_creation((result, records_stats))

        # check update logic
        date = test_date
        result = self.endofdaydata.load_index_derivative_eod_data(date)
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        result = self.livedata.load_index_live_data()
        records_stats = self.livedata.create_or_update(result, IndexLiveData)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_index_live_data()
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_open_interest_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        result = self.livedata.load_index_live_open_interest_data()
        records_stats = self.livedata.create_or_update(result, IndexLiveOpenInterest)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_index_live_open_interest_data()
        assert isinstance(result, str)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_derivative_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        result = self.livedata.load_index_live_derivative_data()
        records_stats = self.livedata.create_or_update(result, IndexLiveDerivativeData)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_index_live_derivative_data()
        assert len(result) == 0

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_option_chain_data(self):
        assert self.exchange is not None
        assert self.exchange.symbol is not None

        result = self.livedata.load_index_live_option_chain_data()
        records_stats = self.livedata.create_or_update(result, IndexLiveOptionChain)
        assert_record_creation((result, records_stats))

        # check update logic
        result = self.livedata.load_index_live_option_chain_data()
        assert len(result) == 0
