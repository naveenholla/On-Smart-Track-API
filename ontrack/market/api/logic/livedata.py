from django.db import transaction

from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.logic.lookup import MarketLookupData
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
from ontrack.utils.base.enum import HolidayCategoryType
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.context import application_context
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

    def __execute_live_data(self, name, module_type, method):
        r = method()
        self.tp.log_message(f"{name} - Data pull completed.", name)

        if isinstance(r, str):
            self.output.append(self.message_creator(name, r))
            self.tp.log_warning(r, name, is_completed=True)
            return

        with transaction.atomic():
            records_stats = self.create_or_update(r, module_type)
            stats = self.message_creator(name, records_stats)
            self.output.append(stats)
            self.tp.log_records_stats(stats, is_completed=True)

    def __execute_live_data_task(
        self,
        name,
        module_type,
        execute_method,
    ):
        self.output = []
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if self.marketlookupdata.exchange() is None:
                message = "Exchange is required."
                self.output.append(self.message_creator(name, message))
                self.tp.log_error(message, name)
                return self.output

            self.tp.log_debug(f"Start Processing - {name}", name)
            try:
                self.__execute_live_data(name, module_type, execute_method)
            except Exception as e:
                message = f"Exception - `{format(e)}`."
                self.tp.log_critical(message=message)
                self.output.append(self.message_creator(name, message))
                raise

            return self.output

    def execute_equity_live_data_task(self):
        name = "Equity Live Data"
        module_type = EquityLiveData
        method = self.load_equity_live_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_equity_open_interest_task(self):
        name = "Equity Open Interest"
        module_type = EquityLiveOpenInterest
        method = self.load_equity_live_open_interest_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_equity_live_derivative_task(self):
        name = "Equity Live Derivative"
        module_type = EquityLiveDerivativeData
        method = self.load_equity_live_derivative_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_equity_option_chain_task(self):
        name = "Equity Option Chain"
        module_type = EquityLiveOptionChain
        method = self.load_equity_live_option_chain_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_index_live_data_task(self):
        name = "Index Live Data"
        module_type = IndexLiveData
        method = self.load_index_live_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_index_open_interest_task(self):
        name = "Index Open Interest"
        module_type = IndexLiveOpenInterest
        method = self.load_index_live_open_interest_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_index_live_derivative_task(self):
        name = "Index Live Derivative"
        module_type = IndexLiveDerivativeData
        method = self.load_index_live_derivative_data

        return self.__execute_live_data_task(name, module_type, method)

    def execute_index_option_chain_task(self):
        name = "Index Option Chain"
        module_type = IndexLiveOptionChain
        method = self.load_index_live_option_chain_data

        return self.__execute_live_data_task(name, module_type, method)
