from datetime import datetime

import pytest

from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.data.initialize import InitializeData
from ontrack.market.models.lookup import Exchange, Index


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_queryset = Exchange.backend.all()
        self.index_queryset = Index.backend.all()

    @pytest.fixture(autouse=True)
    def index_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.initializeData = InitializeData(exchange_fixture.symbol)

        self.initializeData.load_index_data()
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)

    @pytest.mark.lookupdata
    @pytest.mark.integration
    def test_pull_and_parse_index_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.initializeData.load_index_data(False)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 2

        stock = [x for x in result if x["symbol"] == "nifty"][0]
        assert stock["lot_size"] > 0

        stock = [x for x in result if x["symbol"] == "cnxauto"][0]
        assert stock["is_sectoral"]

        index_fixture = self.index_queryset.unique_search(symbol="banknifty").first()
        assert index_fixture is not None and index_fixture.id is not None
        symbol = index_fixture.symbol
        stock2 = [x for x in result if x["symbol"] == symbol][0]
        assert stock2["id"] == index_fixture.id

    @pytest.mark.integration
    def test_pull_parse_index_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = datetime(2022, 10, 20)
        result = self.endofdaydata.load_index_eod_data(date, True)
        assert result is not None
