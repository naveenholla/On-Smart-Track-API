import pytest

from ontrack.market.data.endofdata import EndOfDayData
from ontrack.market.data.initialize import InitializeData
from ontrack.market.data.tests.test_base import test_date
from ontrack.market.models.index import IndexDerivativeEndOfDay, IndexEndOfDay
from ontrack.market.models.lookup import Exchange, Index


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.all()
        self.index_qs = Index.backend.all()
        self.index_eod_qs = IndexEndOfDay.backend.all()
        self.index_derivative_eod_qs = IndexDerivativeEndOfDay.backend.all()

    @pytest.fixture(autouse=True)
    def index_data_fixture(self, exchange_fixture):
        self.exchange_fixture = exchange_fixture
        self.initializeData = InitializeData(exchange_fixture.symbol)

        self.initializeData.load_index_data()
        self.endofdaydata = EndOfDayData(exchange_fixture.symbol)

    @pytest.mark.lookup_data
    @pytest.mark.integration
    def test_pull_and_parse_lookup_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        result = self.initializeData.load_index_data(True)
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        assert len(stocks_with_lot_size) > 2

        stock = [x for x in result if x["symbol"] == "nifty"][0]
        assert stock["lot_size"] > 0

        stock = [x for x in result if x["symbol"] == "cnxauto"][0]
        assert stock["is_sectoral"]

        index_fixture = self.index_qs.unique_search(symbol="banknifty").first()
        assert index_fixture is not None and index_fixture.id is not None
        symbol = index_fixture.symbol
        stock2 = [x for x in result if x["symbol"] == symbol][0]
        assert stock2["id"] == index_fixture.id

        records_count = self.index_qs.all().count()
        assert records_count > 0

        # check update logic
        result = self.initializeData.load_index_data(True)
        assert result is not None
        assert records_count == self.index_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_index_eod_data(date, True)
        assert result is not None

        records_count = self.index_eod_qs.all().count()
        assert records_count > 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_index_eod_data(date, True)
        assert result is not None
        assert records_count == self.index_eod_qs.all().count()

    @pytest.mark.integration
    @pytest.mark.eod_data_pull
    def test_pull_parse_derivative_eod_data(self):
        assert self.exchange_fixture is not None
        assert self.exchange_fixture.symbol is not None

        date = test_date
        result = self.endofdaydata.load_index_derivative_eod_data(date, True)
        assert result is not None

        records_count = self.index_derivative_eod_qs.all().count()
        assert records_count > 0

        # check update logic
        date = test_date
        result = self.endofdaydata.load_index_eod_data(date, True)
        assert result is not None
        assert records_count == self.index_derivative_eod_qs.all().count()
