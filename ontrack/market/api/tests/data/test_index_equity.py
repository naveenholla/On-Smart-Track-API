import pytest

from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.lookup import Equity, EquityIndex, Exchange, Index
from ontrack.utils.config import Configurations


class TestPullEquityIndexData:
    @pytest.fixture(autouse=True)
    def injector(self):
        self.exchange_qs = Exchange.backend.get_queryset()
        self.index_qs = Index.backend.get_queryset()
        self.equity_qs = Equity.backend.get_queryset()
        self.equityindex_qs = EquityIndex.backend.get_queryset()

    @pytest.fixture(autouse=True)
    def equity_index_data_fixture(self, market_lookup_data_fixture: MarketLookupData):
        self.marketlookupdata = market_lookup_data_fixture

    def __pull_indices_market_cap(self, index_symbol):
        urls = Configurations.get_urls_config()
        indices_percentage_urls = urls["indices_percentage"]
        record = [x for x in indices_percentage_urls if x["symbol"] == index_symbol][0]
        weightage_obj = self.marketlookupdata.pull_indices_market_cap(record)

        if "url" not in record:
            assert weightage_obj is None

        else:
            assert weightage_obj is not None
            assert len(weightage_obj) == 2

            records = self.marketlookupdata.parse_indices_market_cap(
                record["symbol"], weightage_obj[0]
            )
            assert records is not None
            assert len(records) > 0

    @pytest.mark.lookup_data
    @pytest.mark.integration
    @pytest.mark.slow
    def test_pull_indices_market_cap_all(self):
        urls = Configurations.get_urls_config()

        indices_percentage_urls = urls["indices_percentage"]
        for record in indices_percentage_urls:
            self.__pull_indices_market_cap(record["symbol"])
