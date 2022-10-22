import pytest

from ontrack.market.models.lookup import Equity, Exchange


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture, equity_fixture, equity_data_fixture):
        self.exchange_fixture = exchange_fixture
        self.equity_fixture = equity_fixture
        self.equity_data_fixture = equity_data_fixture
        self.exchange_queryset = Exchange.backend.all()
        self.equity_queryset = Equity.backend.all()

    @pytest.mark.integration
    def test_pull_and_parse_equity_data_invalid(self):
        result = self.equity_data_fixture("Exchange-not-Exists")
        assert result is None

    @pytest.mark.integration
    def test_pull_and_parse_equity_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.equity_data_fixture(self.exchange_fixture.symbol)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 150

        stock = [x for x in result if x["symbol"].lower() == "hdfcbank"][0]
        assert stock["lot_size"] > 0

        symbol = self.equity_fixture.symbol.lower()
        stock2 = [x for x in result if x["symbol"].lower() == symbol][0]
        assert stock2["id"] == self.equity_fixture.pk
