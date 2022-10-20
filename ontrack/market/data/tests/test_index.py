import pytest

from ontrack.market.data.index import PullIndexData
from ontrack.market.models.lookup import Exchange, Index
from ontrack.utils.config import Configurations


class TestPullIndexData:
    @pytest.fixture(autouse=True)
    def injector(self, exchange_fixture, index_fixture):
        self.exchange_fixture = exchange_fixture
        self.index_fixture = index_fixture

    @pytest.fixture
    def index_data_fixture(self):
        def _method(exchange_symbol):
            exchange_queryset = Exchange.datapull_manager.all()
            index_queryset = Index.datapull_manager.all()
            assert exchange_queryset.count() == 1

            urls = Configurations.get_urls_config()
            indices_percentage = urls["indices_percentage"]
            fo_marketlot = urls["fo_marketlot"]

            pull_index_obj = PullIndexData(
                exchange_queryset,
                index_queryset,
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


# import pytest

# from ontrack.market.logic.data_pull import DataPull
# from ontrack.market.logic.tests.factories import EquityFactory
# from ontrack.utils.config import Configurations
# from ontrack.market.models import Exchange

# class TestDataPull:
#     @pytest.mark.integration
#     @pytest.mark.parametrize(
#         "index_name",
#         [
#             "India Vix",
#             "Nifty 50",
#             "Nifty Total Market",
#             "Nifty Bank",
#             "Nifty Pharma",
#             "Nifty Realty",
#         ],
#     )
#     def test_pull_indices_market_cap(self, equity_fixture:EquityFactory, index_name):
#         obj = equity_fixture.create_batch()
#         assert Exchange.objects.all().count() > 0

#         urls = Configurations.get_urls_config()

#         datapull_obj = DataPull()
#         indices_percentage_urls = urls["indices_percentage"]
#         record = [x for x in indices_percentage_urls if x["name"] == index_name][0]
#         weightage_obj = datapull_obj.pull_indices_market_cap(record)
#         index_record = datapull_obj.parse_index_data("NSE", record)

#         if "url" not in record:
#             assert index_record is not None
#             assert index_record["name"] == index_name

#             assert weightage_obj is None

#         else:
#             assert index_record is not None
#             assert index_record["name"] == index_name

#             assert weightage_obj is not None
#             assert len(weightage_obj) == 2

#             records = datapull_obj.parse_indices_market_cap(
#                 record["name"], weightage_obj[0]
#             )
#             assert records is not None
#             assert len(records) > 0


#     @pytest.mark.integration
#     @pytest.mark.slow
#     def test_pull_indices_market_cap_all():
#         urls = Configurations.get_urls_config()

#         indices_percentage_urls = urls["indices_percentage"]
#         for record in indices_percentage_urls:
#             test_pull_indices_market_cap(record["name"])
