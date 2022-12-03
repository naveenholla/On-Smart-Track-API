from django.shortcuts import render

from ontrack.market.tasks.equity import execute_equity_eod_data_task
from ontrack.market.tasks.index import execute_indices_eod_data_task
from ontrack.market.tasks.lookup import execute_market_lookup_data_task
from ontrack.market.tasks.participant import execute_participant_eod_data_task


def task_execution_view(request, task_name):
    new_celery_task = None
    if task_name == "equity_lookup":
        new_celery_task = execute_market_lookup_data_task.delay()

    if task_name == "equity_eod":
        new_celery_task = execute_equity_eod_data_task.delay()

    if task_name == "index_eod":
        new_celery_task = execute_indices_eod_data_task.delay()

    if task_name == "participant_eod":
        new_celery_task = execute_participant_eod_data_task.delay()

    if not new_celery_task:
        return render(request, "404.html")

    return render(request, "market/task.html", {"task_id": new_celery_task.task_id})
