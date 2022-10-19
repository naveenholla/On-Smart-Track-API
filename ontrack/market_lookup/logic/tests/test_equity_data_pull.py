from ontrack.market_lookup.logic.data_pull import PullEquityData
from ontrack.market_lookup.logic.tests.factories import EquityFactory, ExchangeFactory
from ontrack.market_lookup.models import Equity, Exchange
from ontrack.utils.config import Configurations


class TestPullEquityData:
    def test_pull_and_parse_equity_data_exchange_None(self):
        pull_equity_obj = PullEquityData()
        result = pull_equity_obj.pull_and_parse_equity_data(
            None, "Url", "Market Cap Url"
        )
        assert result is None

    def test_pull_and_parse_equity_data_url_None(self):
        pull_equity_obj = PullEquityData()
        result = pull_equity_obj.pull_and_parse_equity_data(
            "Exchange", None, "Market Cap Url"
        )
        assert result is None

    def test_pull_and_parse_equity_data_market_url_none(self):
        pull_equity_obj = PullEquityData()
        result = pull_equity_obj.pull_and_parse_equity_data("Exchange", "Url", None)
        assert result is None

    def test_pull_and_parse_equity_data_Exchange_Not_Exists(
        self, equity_fixture: EquityFactory, exchange_fixture: ExchangeFactory
    ):
        exchange_queryset = Exchange.datapull_manager.all()
        assert exchange_queryset.count() == 1

        pull_equity_obj = PullEquityData(exchange_queryset)
        result = pull_equity_obj.pull_and_parse_equity_data(
            "Exchange-not-Exists", "Url", None
        )
        assert result is None

    def test_pull_and_parse_equity_data_Exchange(
        self, equity_fixture: EquityFactory, exchange_fixture: ExchangeFactory
    ):
        exchange_queryset = Exchange.datapull_manager.all()
        equity_queryset = Equity.datapull_manager.all()
        assert exchange_queryset.count() == 1

        urls = Configurations.get_urls_config()
        listed_equities = urls["listed_equities"]
        fo_marketlot = urls["fo_marketlot"]

        pull_equity_obj = PullEquityData(exchange_queryset, equity_queryset)
        result = pull_equity_obj.pull_and_parse_equity_data(
            exchange_fixture.symbol, listed_equities, fo_marketlot
        )
        assert result is not None

        stocks_with_lot_size = [x for x in result if x["lot_size"] > 0]
        stock = [x for x in result if x["symbol"].lower() == "hdfcbank"][0]
        stock2 = [
            x for x in result if x["symbol"].lower() == equity_fixture.symbol.lower()
        ][0]

        assert len(stocks_with_lot_size) > 150
        assert stock["lot_size"] > 0
        assert stock2["id"] == equity_fixture.pk
