import pytest

from ontrack.market.data.common import CommonDataPull
from ontrack.market.data.index import PullIndexData
from ontrack.market.models.lookup import Exchange, Index
from ontrack.utils.config import Configurations


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture, index_fixture):
        self.exchange_fixture = exchange_fixture
        self.index_fixture = index_fixture
        self.exchange_queryset = Exchange.datapull_manager.all()
        self.index_queryset = Index.datapull_manager.all()

    @pytest.fixture
    def index_data_fixture(self):
        def _method(exchange_symbol):
            assert self.exchange_queryset.count() == 1

            urls = Configurations.get_urls_config()
            indices_percentage = urls["indices_percentage"]
            fo_marketlot = urls["fo_marketlot"]

            pull_index_obj = PullIndexData(
                self.exchange_queryset,
                self.index_queryset,
                indices_percentage,
                fo_marketlot,
                exchange_symbol,
            )
            return pull_index_obj.pull_and_parse_indice_data()

        return _method

    def test_pull_and_parse_index_data_invalid(self, index_data_fixture):
        result = index_data_fixture("Exchange-not-Exists")
        assert result is None

    def test_pull_and_parse_index_data(self, index_data_fixture):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = index_data_fixture(self.exchange_fixture.symbol)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 2

        stock = [x for x in result if x["symbol"].lower() == "nifty"][0]
        assert stock["lot_size"] > 0

        stock = [x for x in result if x["symbol"].lower() == "cnxauto"][0]
        assert stock["is_sectoral"]

        symbol = self.index_fixture.symbol.lower()
        stock2 = [x for x in result if x["symbol"].lower() == symbol][0]
        assert stock2["id"] == self.index_fixture.pk

        CommonDataPull().create_or_update(result, Index, Index.datapull_manager)

        assert self.index_queryset.count() == len(result)
