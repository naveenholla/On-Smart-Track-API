from time import sleep

from config import celery_app
from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.utils.base.enum import ExchangeType
from ontrack.utils.base.tasks import TaskProgressRecorder


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_equity_eod_data_task(self) -> str:
    """This task is used to pull_equity_eod_data from the website"""
    sleep(1)
    recorder = TaskProgressRecorder(self)
    return EndOfDayData(ExchangeType.NSE, recorder).execute_equity_eod_data_task()
