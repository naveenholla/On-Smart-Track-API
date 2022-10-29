from ontrack.market.data.common import CommonData
from ontrack.market.data.equity import PullEquityData
from ontrack.market.data.index import PullIndexData
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
from ontrack.utils.logger import ApplicationLogger


class LiveData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonData()
        self.exchange_symbol = exchange_symbol

    def load_equity_live_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        equity_qs = Equity.backend.get_queryset()
        equity_liveData_qs = EquityLiveData.backend.get_queryset()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
            equity_live_qs=equity_liveData_qs,
        )

        result = pull_equity_obj.pull_parse_live_data()
        if save_data:
            self.commonobj.create_or_update(result, EquityLiveData)

        return result

    def load_index_live_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        index_qs = Index.backend.get_queryset()
        index_liveData_qs = IndexLiveData.backend.get_queryset()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
            index_live_qs=index_liveData_qs,
        )

        result = pull_index_obj.pull_parse_live_data()
        if save_data:
            self.commonobj.create_or_update(result, IndexLiveData)

        return result

    def load_equity_live_open_interest_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        equity_qs = Equity.backend.get_queryset()
        equity_live_open_interest_qs = EquityLiveOpenInterest.backend.get_queryset()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
            equity_live_open_interest_qs=equity_live_open_interest_qs,
        )

        result = pull_equity_obj.pull_parse_live_open_interest_data()
        if save_data:
            self.commonobj.create_or_update(result, EquityLiveOpenInterest)

        return result

    def load_index_live_open_interest_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        index_qs = Index.backend.get_queryset()
        index_live_open_interest_qs = IndexLiveOpenInterest.backend.get_queryset()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
            index_live_open_interest_qs=index_live_open_interest_qs,
        )

        result = pull_index_obj.pull_parse_live_open_interest_data()
        if save_data:
            self.commonobj.create_or_update(result, IndexLiveOpenInterest)

        return result

    def load_index_live_derivative_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        index_qs = Index.backend.get_queryset()
        index_live_derivative_qs = IndexLiveDerivativeData.backend.get_queryset()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
            index_live_derivative_qs=index_live_derivative_qs,
        )

        result = pull_index_obj.pull_parse_live_derivative_data()
        if save_data:
            self.commonobj.create_or_update(result, IndexLiveDerivativeData)

        return result

    def load_equity_live_derivative_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        equity_qs = Equity.backend.get_queryset()
        equity_live_derivative_qs = EquityLiveDerivativeData.backend.get_queryset()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
            equity_live_derivative_qs=equity_live_derivative_qs,
        )

        result = pull_equity_obj.pull_parse_live_derivative_data()
        if save_data:
            self.commonobj.create_or_update(result, EquityLiveDerivativeData)

        return result

    def load_index_live_option_chain_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        index_qs = Index.backend.get_queryset()
        index_live_option_chain_qs = IndexLiveOptionChain.backend.get_queryset()

        pull_index_obj = PullIndexData(
            self.exchange_symbol,
            exchange_qs,
            index_qs,
            index_live_option_chain_qs=index_live_option_chain_qs,
        )

        result = pull_index_obj.pull_parse_live_option_chain_data()
        if save_data:
            self.commonobj.create_or_update(result, IndexLiveOptionChain)

        return result

    def load_equity_live_option_chain_data(self, save_data=True):
        exchange_qs = Exchange.backend.get_queryset()
        equity_qs = Equity.backend.get_queryset()
        equity_live_option_chain_qs = EquityLiveOptionChain.backend.get_queryset()

        pull_equity_obj = PullEquityData(
            self.exchange_symbol,
            exchange_qs,
            equity_qs,
            equity_live_option_chain_qs=equity_live_option_chain_qs,
        )

        result = pull_equity_obj.pull_parse_live_option_chain_data()
        if save_data:
            self.commonobj.create_or_update(result, EquityLiveOptionChain)

        return result

    def load_live_data(self):
        self.load_equity_live_data()
        self.load_index_live_data()

        self.load_equity_live_open_interest_data()
        self.load_index_live_open_interest_data()

        self.load_equity_live_derivative_data()
        self.load_index_live_derivative_data()

        self.load_equity_live_option_chain_data()
        self.load_index_live_option_chain_data()
