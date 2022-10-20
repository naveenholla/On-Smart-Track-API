from config import celery_app

from ..logic.equity_endofdata import EquityDataPullLogic


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def pull_equity_eod_data(self) -> str:
    """This task is used to pull_equity_eod_data from the website"""
    return EquityDataPullLogic().execute_pull_equity_eod_data_task()
