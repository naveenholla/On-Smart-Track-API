from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.logger import ApplicationLogger


class LiveData(BaseLogic):
    def __init__(self, exchange_symbol, recorder=None):
        self.logger = ApplicationLogger()
        self.marketlookupdata = MarketLookupData(exchange_symbol)

        tp = TaskProgressStatus(recorder)
        self.tp = tp

        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        inx = self.marketlookupdata.index_dict()

        self.pull_equity_obj = PullEquityData(ex, eq, tp)
        self.pull_index_obj = PullIndexData(ex, inx, tp)

    def load_equity_live_data(self):
        return self.pull_equity_obj.pull_parse_live_data()

    def load_index_live_data(self):
        return self.pull_index_obj.pull_parse_live_data()

    def load_equity_live_open_interest_data(self):
        return self.pull_equity_obj.pull_parse_live_open_interest_data()

    def load_index_live_open_interest_data(self):
        return self.pull_index_obj.pull_parse_live_open_interest_data()

    def load_index_live_derivative_data(self):
        return self.pull_index_obj.pull_parse_live_derivative_data()

    def load_equity_live_derivative_data(self):
        return self.pull_equity_obj.pull_parse_live_derivative_data()

    def load_index_live_option_chain_data(self):
        return self.pull_index_obj.pull_parse_live_option_chain_data()

    def load_equity_live_option_chain_data(self):
        return self.pull_equity_obj.pull_parse_live_option_chain_data()
