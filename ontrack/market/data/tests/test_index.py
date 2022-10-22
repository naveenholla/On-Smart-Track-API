import pytest

from ontrack.market.models.lookup import Exchange, Index


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture, index_fixture, index_data_fixture):
        self.exchange_fixture = exchange_fixture
        self.index_fixture = index_fixture
        self.index_data_fixture = index_data_fixture
        self.exchange_queryset = Exchange.backend.all()
        self.index_queryset = Index.backend.all()

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_and_parse_index_data_invalid(self):
        result = self.index_data_fixture("Exchange-not-Exists")
        assert result is None

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_and_parse_index_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.index_data_fixture(self.exchange_fixture.symbol)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 2

        stock = [x for x in result if x["symbol"] == "nifty"][0]
        assert stock["lot_size"] > 0

        stock = [x for x in result if x["symbol"] == "cnxauto"][0]
        assert stock["is_sectoral"]

        symbol = self.index_fixture.symbol
        stock2 = [x for x in result if x["symbol"] == symbol][0]
        assert stock2["id"] == self.index_fixture.pk
