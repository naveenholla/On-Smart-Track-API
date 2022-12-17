from config import celery_app
from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.api.logic.livedata import LiveData
from ontrack.market.tasks.base import execute_task
from ontrack.utils.base.enum import ExchangeType
from ontrack.utils.base.tasks import TaskProgressRecorder


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_equity_eod_data_task(self, websocket_enabled=False) -> str:
    recorder = TaskProgressRecorder(self, websocket_enabled)

    ex = ExchangeType.NSE
    obj = EndOfDayData(ex, recorder)
    method = obj.execute_equity_eod_data_task

    return execute_task(self, method)


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_equity_live_data_task(self, websocket_enabled=False) -> str:
    recorder = TaskProgressRecorder(self, websocket_enabled)

    ex = ExchangeType.NSE
    obj = LiveData(ex, recorder)
    method = obj.execute_equity_live_data_task

    return execute_task(self, method)


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_equity_live_derivative_task(self, websocket_enabled=False) -> str:
    recorder = TaskProgressRecorder(self, websocket_enabled)

    ex = ExchangeType.NSE
    obj = LiveData(ex, recorder)
    method = obj.execute_equity_live_derivative_task

    return execute_task(self, method)


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_equity_option_chain_task(self, websocket_enabled=False) -> str:
    recorder = TaskProgressRecorder(self, websocket_enabled)

    ex = ExchangeType.NSE
    obj = LiveData(ex, recorder)
    method = obj.execute_equity_option_chain_task

    return execute_task(self, method)


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_equity_open_interest_task(self, websocket_enabled=False) -> str:
    recorder = TaskProgressRecorder(self, websocket_enabled)

    ex = ExchangeType.NSE
    obj = LiveData(ex, recorder)
    method = obj.execute_equity_open_interest_task

    return execute_task(self, method)


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_delete_old_data_task(self, websocket_enabled=False) -> str:
    recorder = TaskProgressRecorder(self, websocket_enabled)

    ex = ExchangeType.NSE
    obj = LiveData(ex, recorder)
    method = obj.execute_delete_old_data_task

    return execute_task(self, method)
