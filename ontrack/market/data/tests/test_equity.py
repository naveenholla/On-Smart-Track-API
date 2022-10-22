import pytest

from ontrack.market.data.initialize import InitializeData
from ontrack.market.data.tests.factories import EquityFactory
from ontrack.market.models.lookup import Equity, Exchange


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.exchange_queryset = Exchange.backend.all()
        self.equity_queryset = Equity.backend.all()

        self.initializeData = InitializeData()

    @pytest.fixture(autouse=True)
    def equity_fixture(self) -> Equity:
        self.equity_fixture = EquityFactory()
        return self.equity_fixture

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_and_parse_equity_data_invalid(self):
        result = self.initializeData.load_equity_data("Exchange-not-Exists", False)
        assert result is None

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_and_parse_equity_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        es = self.exchange_fixture.symbol
        result = self.initializeData.load_equity_data(es, False)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 150

        stock = [x for x in result if x["symbol"] == "hdfcbank"][0]
        assert stock["lot_size"] > 0

        symbol = self.equity_fixture.symbol
        stock2 = [x for x in result if x["symbol"] == symbol][0]
        assert stock2["id"] == self.equity_fixture.pk
