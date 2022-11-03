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
from ontrack.market.models.lookup import Exchange, Index


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()
        self.index_qs = Index.backend.get_queryset()
        self.index_eod_qs = IndexEndOfDay.backend.get_queryset()
        self.index_derivative_eod_qs = IndexDerivativeEndOfDay.backend.get_queryset()
        self.index_live_data_qs = IndexLiveData.backend.get_queryset()
        self.index_live_open_interest_qs = IndexLiveOpenInterest.backend.get_queryset()
        self.index_live_derivative_qs = IndexLiveDerivativeData.backend.get_queryset()
        self.index_live_option_chain_qs = IndexLiveOptionChain.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def index_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.marketlookupdata = MarketLookupData(exchange_fixture.symbol)

        self.marketlookupdata.load_index_data()
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)
        self.livedata = LiveData(exchange_fixture.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.marketlookupdata.load_index_data(True)
        assert result is not None
        records = result[0]
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
        result = self.marketlookupdata.load_index_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_index_eod_data(date, True)
        assert_record_creation(result)

        # check update logic
        date = test_date
        result = self.endofdaydata.load_index_eod_data(date, True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_index_derivative_eod_data(date, True)
        assert_record_creation(result)

        # check update logic
        date = test_date
        result = self.endofdaydata.load_index_derivative_eod_data(date, True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_index_live_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_index_live_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_open_interest_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_index_live_open_interest_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_index_live_open_interest_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_derivative_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_index_live_derivative_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_index_live_derivative_data(True)
        assert_record_updation(result)

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_option_chain_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_index_live_option_chain_data(True)
        assert_record_creation(result)

        # check update logic
        result = self.livedata.load_index_live_option_chain_data(True)
        assert_record_updation(result)
