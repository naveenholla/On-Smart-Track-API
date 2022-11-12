from config import celery_app
from ontrack.lookup.api.logic.lookup import InitializeData


@celery_app.task(bind=True)
def execute_initial_lookup_data_task(self) -> str:
    """This task is used to execute initial lookup data task from the website"""
    return InitializeData().execute_initial_lookup_data_task()
