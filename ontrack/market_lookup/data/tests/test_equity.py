import pytest

from ontrack.market_lookup.data.equity import PullEquityData
from ontrack.market_lookup.models.lookup import Equity, Exchange
from ontrack.utils.config import Configurations


class TestPullEquityData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture, equity_fixture):
        self.exchange_fixture = exchange_fixture
        self.equity_fixture = equity_fixture

    @pytest.fixture
    def equity_data_fixture(self):
        def _method(exchange_symbol):
            exchange_queryset = Exchange.datapull_manager.all()
            equity_queryset = Equity.datapull_manager.all()
            assert exchange_queryset.count() == 1

            urls = Configurations.get_urls_config()
            listed_equities = urls["listed_equities"]
            fo_marketlot = urls["fo_marketlot"]

            pull_equity_obj = PullEquityData(
                exchange_queryset,
                equity_queryset,
                listed_equities,
                fo_marketlot,
                exchange_symbol,
            )
            return pull_equity_obj.pull_and_parse_equity_data()

        return _method

    def test_pull_and_parse_equity_data_invalid(self, equity_data_fixture):
        result = equity_data_fixture("Exchange-not-Exists")
        assert result is None

    def test_pull_and_parse_equity_data(self, equity_data_fixture):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = equity_data_fixture(self.exchange_fixture.symbol)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        stock = [x for x in result if x["symbol"].lower() == "hdfcbank"][0]

        symbol = self.equity_fixture.symbol.lower()
        stock2 = [x for x in result if x["symbol"].lower() == symbol][0]

        assert len(stocks_with_lot_size) > 150
        assert stock["lot_size"] > 0
        assert stock2["id"] == self.equity_fixture.pk
