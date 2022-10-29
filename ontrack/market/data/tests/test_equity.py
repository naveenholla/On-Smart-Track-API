import pytest

from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.data.initialize import InitializeData
from ontrack.market.data.livedata import LiveData
from ontrack.market.data.tests.test_base import test_date
from ontrack.market.models.equity import (
    EquityDerivativeEndOfDay,
    EquityEndOfDay,
    EquityLiveData,
    EquityLiveDerivativeData,
    EquityLiveOpenInterest,
    EquityLiveOptionChain,
)
from ontrack.market.models.lookup import Equity, Exchange


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.all()
        self.equity_qs = Equity.backend.all()
        self.equity_eod_qs = EquityEndOfDay.backend.all()
        self.equity_derivative_eod_qs = EquityDerivativeEndOfDay.backend.all()
        self.equity_live_data_qs = EquityLiveData.backend.all()
        self.equity_live_open_interest_qs = EquityLiveOpenInterest.backend.all()
        self.equity_live_derivative_qs = EquityLiveDerivativeData.backend.all()
        self.equity_live_option_chain_qs = EquityLiveOptionChain.backend.all()

    @pytest.fixture(autouse=True)
    def equity_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.initializeData = InitializeData(exchange_fixture.symbol)

        self.initializeData.load_equity_data()
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)
        self.livedata = LiveData(exchange_fixture.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.initializeData.load_equity_data(True)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 150

        stock = [x for x in result if x["symbol"] == "hdfcbank"][0]
        assert stock["lot_size"] > 0

        equity_fixture = self.equity_qs.unique_search(symbol="reliance").first()
        assert equity_fixture is not None and equity_fixture.id is not None
        symbol = equity_fixture.symbol
        stock2 = [x for x in result if x["symbol"] == symbol][0]
        assert stock2["id"] == equity_fixture.id

        records_count = self.equity_qs.all().count()
        assert records_count > 0

        # check update logic
        result = self.initializeData.load_equity_data(True)
        assert result is not None
        assert records_count == self.equity_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date, True)
        assert result is not None

        records_count = self.equity_eod_qs.all().count()
        assert records_count > 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date, True)
        assert result is not None
        assert records_count == self.equity_eod_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_equity_derivative_eod_data(date, True)
        assert result is not None

        records_count = self.equity_derivative_eod_qs.all().count()
        assert records_count > 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_equity_eod_data(date, True)
        assert result is not None
        assert records_count == self.equity_derivative_eod_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_data(True)
        assert result is not None

        records_count = self.equity_live_data_qs.all().count()
        assert records_count > 0

        # check update logic
        result = self.livedata.load_equity_live_data(True)
        assert result is not None
        assert records_count == self.equity_live_data_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_open_interest_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_open_interest_data(True)
        assert result is not None

        records_count = self.equity_live_open_interest_qs.all().count()
        assert records_count > 0

        # check update logic
        result = self.livedata.load_equity_live_open_interest_data(True)
        assert result is not None
        assert records_count == self.equity_live_open_interest_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_derivative_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_derivative_data(True)
        assert result is not None

        records_count = self.equity_live_derivative_qs.all().count()
        assert records_count > 0

        # check update logic
        result = self.livedata.load_equity_live_derivative_data(True)
        assert result is not None
        assert records_count == self.equity_live_derivative_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.live_data_pull
    def test_pull_parse_live_option_chain_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.livedata.load_equity_live_option_chain_data(True)
        assert result is not None

        records_count = self.equity_live_option_chain_qs.all().count()
        assert records_count > 0

        # check update logic
        result = self.livedata.load_equity_live_option_chain_data(True)
        assert result is not None
        assert records_count == self.equity_live_option_chain_qs.all().count()
