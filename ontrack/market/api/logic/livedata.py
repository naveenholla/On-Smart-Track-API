from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.models.lookup import Equity, Exchange, Index
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.logger import ApplicationLogger


class LiveData(BaseLogic):
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()

        exchange_qs = Exchange.backend.get_queryset()
        self.exchange = exchange_qs.unique_search(exchange_symbol).first()

        equity_qs = Equity.backend.get_queryset()
        self.equity_dict = self.create_dict(equity_qs)

        index_qs = Index.backend.get_queryset()
        self.index_dict = self.create_dict(index_qs, "name")

        self.pull_equity_obj = PullEquityData(self.exchange, self.equity_dict)
        self.pull_index_obj = PullIndexData(self.exchange, self.index_dict)

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
