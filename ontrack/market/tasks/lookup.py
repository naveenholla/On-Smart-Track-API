from celery_progress.backend import ProgressRecorder

from config import celery_app
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.utils.base.enum import ExchangeType


@celery_app.task(bind=True)
def execute_initial_lookup_data_task(self) -> str:
    """This task is used to execute initial lookup data task from the website"""
    return MarketLookupData(ExchangeType.NSE).execute_initial_lookup_data_task()


@celery_app.task(bind=True)
def execute_holidays_lookup_data_task(self) -> str:
    """This task is used to execute initial lookup data task from the website"""
    return MarketLookupData(ExchangeType.NSE).execute_holidays_lookup_data_task()


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_market_lookup_data_task(self) -> str:
    """This task is used to pull the indices data from the website"""
    recorder = ProgressRecorder(self)
    return MarketLookupData(ExchangeType.NS, recorder).execute_market_lookup_data_task()
