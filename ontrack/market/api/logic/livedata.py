from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.logger import ApplicationLogger


class LiveData(BaseLogic):
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.marketlookupdata = MarketLookupData(exchange_symbol)

    def load_equity_live_data(self):
        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        obj = PullEquityData(ex, eq)
        return obj.pull_parse_live_data()

    def load_index_live_data(self):
        ex = self.marketlookupdata.exchange()
        inx = self.marketlookupdata.index_dict()
        obj = PullIndexData(ex, inx)
        return obj.pull_parse_live_data()

    def load_equity_live_open_interest_data(self):
        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        obj = PullEquityData(ex, eq)
        return obj.pull_parse_live_open_interest_data()

    def load_index_live_open_interest_data(self):
        ex = self.marketlookupdata.exchange()
        inx = self.marketlookupdata.index_dict()
        obj = PullIndexData(ex, inx)
        return obj.pull_parse_live_open_interest_data()

    def load_index_live_derivative_data(self):
        ex = self.marketlookupdata.exchange()
        inx = self.marketlookupdata.index_dict()
        obj = PullIndexData(ex, inx)
        return obj.pull_parse_live_derivative_data()

    def load_equity_live_derivative_data(self):
        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        obj = PullEquityData(ex, eq)
        return obj.pull_parse_live_derivative_data()

    def load_index_live_option_chain_data(self):
        ex = self.marketlookupdata.exchange()
        inx = self.marketlookupdata.index_dict()
        obj = PullIndexData(ex, inx)
        return obj.pull_parse_live_option_chain_data()

    def load_equity_live_option_chain_data(self):
        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        obj = PullEquityData(ex, eq)
        return obj.pull_parse_live_option_chain_data()
