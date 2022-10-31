from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.models.equity import (
    EquityLiveData,
    EquityLiveDerivativeData,
    EquityLiveOpenInterest,
    EquityLiveOptionChain,
)
from ontrack.market.models.index import (
    IndexLiveData,
    IndexLiveDerivativeData,
    IndexLiveOpenInterest,
    IndexLiveOptionChain,
)
from ontrack.market.models.lookup import Equity, Exchange, Index
from ontrack.utils.base.manager import CommonLogic
from ontrack.utils.logger import ApplicationLogger


class LiveData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonLogic()
        self.exchange_symbol = exchange_symbol

        self.exchange_qs = Exchange.backend.get_queryset()
        self.equity_qs = Equity.backend.get_queryset()
        self.index_qs = Index.backend.get_queryset()

        self.equity_liveData_qs = EquityLiveData.backend.get_queryset()
        self.index_liveData_qs = IndexLiveData.backend.get_queryset()

        self.equity_live_open_interest_qs = (
            EquityLiveOpenInterest.backend.get_queryset()
        )
        self.index_live_open_interest_qs = IndexLiveOpenInterest.backend.get_queryset()

        self.index_live_derivative_qs = IndexLiveDerivativeData.backend.get_queryset()
        self.equity_live_derivative_qs = EquityLiveDerivativeData.backend.get_queryset()

        self.index_live_option_chain_qs = IndexLiveOptionChain.backend.get_queryset()
        self.equity_live_option_chain_qs = EquityLiveOptionChain.backend.get_queryset()

    def load_equity_live_data(self, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            self.exchange_qs,
            self.equity_qs,
            equity_live_qs=self.equity_liveData_qs,
        )

        result = pull_equity_obj.pull_parse_live_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(result, EquityLiveData)

        return result, records_stats

    def load_index_live_data(self, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            self.exchange_qs,
            self.index_qs,
            index_live_qs=self.index_liveData_qs,
        )

        result = pull_index_obj.pull_parse_live_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(result, IndexLiveData)

        return result, records_stats

    def load_equity_live_open_interest_data(self, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            self.exchange_qs,
            self.equity_qs,
            equity_live_open_interest_qs=self.equity_live_open_interest_qs,
        )

        result = pull_equity_obj.pull_parse_live_open_interest_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(
                result, EquityLiveOpenInterest
            )

        return result, records_stats

    def load_index_live_open_interest_data(self, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            self.exchange_qs,
            self.index_qs,
            index_live_open_interest_qs=self.index_live_open_interest_qs,
        )

        result = pull_index_obj.pull_parse_live_open_interest_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(
                result, IndexLiveOpenInterest
            )

        return result, records_stats

    def load_index_live_derivative_data(self, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            self.exchange_qs,
            self.index_qs,
            index_live_derivative_qs=self.index_live_derivative_qs,
        )

        result = pull_index_obj.pull_parse_live_derivative_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(
                result, IndexLiveDerivativeData
            )

        return result, records_stats

    def load_equity_live_derivative_data(self, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            self.exchange_qs,
            self.equity_qs,
            equity_live_derivative_qs=self.equity_live_derivative_qs,
        )

        result = pull_equity_obj.pull_parse_live_derivative_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(
                result, EquityLiveDerivativeData
            )

        return result, records_stats

    def load_index_live_option_chain_data(self, save_data=True):
        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            self.exchange_qs,
            self.index_qs,
            index_live_option_chain_qs=self.index_live_option_chain_qs,
        )

        result = pull_index_obj.pull_parse_live_option_chain_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(
                result, IndexLiveOptionChain
            )

        return result, records_stats

    def load_equity_live_option_chain_data(self, save_data=True):
        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            self.exchange_qs,
            self.equity_qs,
            equity_live_option_chain_qs=self.equity_live_option_chain_qs,
        )

        result = pull_equity_obj.pull_parse_live_option_chain_data()
        if save_data:
            records_stats = self.commonobj.create_or_update(
                result, EquityLiveOptionChain
            )

        return result, records_stats

    def load_live_data(self):
        self.load_equity_live_data()
        self.load_index_live_data()

        self.load_equity_live_open_interest_data()
        self.load_index_live_open_interest_data()

        self.load_equity_live_derivative_data()
        self.load_index_live_derivative_data()

        self.load_equity_live_option_chain_data()
        self.load_index_live_option_chain_data()
