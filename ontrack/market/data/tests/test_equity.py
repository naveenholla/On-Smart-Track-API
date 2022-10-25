from datetime import datetime

import pytest

from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.data.initialize import InitializeData
from ontrack.market.models.lookup import Equity, Exchange


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_queryset = Exchange.backend.all()
        self.equity_queryset = Equity.backend.all()

    @pytest.fixture(autouse=True)
    def equity_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.initializeData = InitializeData(exchange_fixture.symbol)

        self.initializeData.load_equity_data()
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.initializeData.load_equity_data(False)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 150

        stock = [x for x in result if x["symbol"] == "hdfcbank"][0]
        assert stock["lot_size"] > 0

        equity_fixture = self.equity_queryset.unique_search(symbol="reliance").first()
        assert equity_fixture is not None and equity_fixture.id is not None
        symbol = equity_fixture.symbol
        stock2 = [x for x in result if x["symbol"] == symbol][0]
        assert stock2["id"] == equity_fixture.id

    @pytest.mark.integration
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = datetime(2022, 10, 20)
        result = self.endofdaydata.load_equity_eod_data(date, True)
        assert result is not None

    @pytest.mark.integration
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = datetime(2022, 10, 20)
        result = self.endofdaydata.load_equity_derivative_eod_data(date, True)
        assert result is not None
