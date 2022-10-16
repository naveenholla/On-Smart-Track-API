from config import celery_app

from .logic.endofdata import IndicesDataPullLogic


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def pull_indices_eod_data(self) -> str:
    """This task is used to pull_equity_eod_data from the website"""
    return IndicesDataPullLogic().execute_pull_indices_eod_data_task()
