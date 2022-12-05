from django.shortcuts import render

from ontrack.market.tasks.equity import (
    execute_equity_eod_data_task,
    execute_equity_live_data_task,
    execute_equity_live_derivative_task,
    execute_equity_open_interest_task,
    execute_equity_option_chain_task,
)
from ontrack.market.tasks.index import (
    execute_index_eod_data_task,
    execute_index_live_data_task,
    execute_index_live_derivative_task,
    execute_index_open_interest_task,
    execute_index_option_chain_task,
)
from ontrack.market.tasks.lookup import execute_market_lookup_data_task
from ontrack.market.tasks.participant import execute_participant_eod_data_task


def task_execution_view(request, task_name):
    new_celery_task = None
    if task_name == "equity_lookup":
        new_celery_task = execute_market_lookup_data_task.delay(True)

    if task_name == "equity_eod":
        new_celery_task = execute_equity_eod_data_task.delay(True)

    if task_name == "index_eod":
        new_celery_task = execute_index_eod_data_task.delay(True)

    if task_name == "participant_eod":
        new_celery_task = execute_participant_eod_data_task.delay(True)

    if task_name == "equity_live":
        new_celery_task = execute_equity_live_data_task.delay(True)

    if task_name == "equity_open_interest":
        new_celery_task = execute_equity_open_interest_task.delay(True)

    if task_name == "equity_derivative":
        new_celery_task = execute_equity_live_derivative_task.delay(True)

    if task_name == "equity_option_chain":
        new_celery_task = execute_equity_option_chain_task.delay(True)

    if task_name == "index_live":
        new_celery_task = execute_index_live_data_task.delay(True)

    if task_name == "index_open_interest":
        new_celery_task = execute_index_open_interest_task.delay(True)

    if task_name == "index_derivative":
        new_celery_task = execute_index_live_derivative_task.delay(True)

    if task_name == "index_option_chain":
        new_celery_task = execute_index_option_chain_task.delay(True)

    if not new_celery_task:
        return render(request, "404.html")

    return render(request, "market/task.html", {"task_id": new_celery_task.task_id})
