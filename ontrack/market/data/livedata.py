from ontrack.market.data.common import CommonData
from ontrack.market.data.equity import PullEquityData
from ontrack.market.models.equity import EquityLiveData
from ontrack.market.models.lookup import Equity, Exchange
from ontrack.utils.logger import ApplicationLogger


class LiveData:
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.commonobj = CommonData()
        self.exchange_symbol = exchange_symbol

    def load_equity_live_data(self, save_data=True):
        exchange_qs = Exchange.backend.all()
        equity_qs = Equity.backend.all()
        equity_liveData_qs = EquityLiveData.backend.all()

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

    def load_live_data(self):
        self.load_equity_live_data()
