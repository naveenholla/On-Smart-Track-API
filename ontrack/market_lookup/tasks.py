from config import celery_app

from .logic.initial import InitialDataPullLogic
from .logic.lookup import LookupDataPullLogic


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def create_intial_market_lookup_data_task(self) -> str:
    """This task is used to pull the indices data from the website"""
    return InitialDataPullLogic().execute_intial_market_lookup_data_task()


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def create_lookup_data_files(self) -> str:
    """This task is used to pull the indices data from the website"""
    return LookupDataPullLogic().execute_create_lookup_data_files()


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def pull_equity_lookup_data(self) -> str:
    """This task is used to pull the indices data from the website"""
    return LookupDataPullLogic().execute_equity_lookup_data_task()
