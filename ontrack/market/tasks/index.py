from time import sleep

from config import celery_app
from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.utils.base.enum import ExchangeType
from ontrack.utils.base.tasks import TaskProgressRecorder
from ontrack.utils.context import memcache_lock


@celery_app.task(bind=True, soft_time_limit=10000, time_limit=15000)
def execute_indices_eod_data_task(self) -> str:
    """This task is used to execute_indices_eod_data_task from the website"""
    lock_id = f"{self.name}-lock"
    print(lock_id)
    print(self.app.oid)

    recorder = TaskProgressRecorder(self)
    with memcache_lock(lock_id, self.app.oid) as acquired:
        if acquired:
            sleep(1)
            ex = ExchangeType.NSE
            obj = EndOfDayData(ex, recorder)
            return obj.execute_index_eod_data_task()

    return f"Task {self.name} is already being running by another worker."
