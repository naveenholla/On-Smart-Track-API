from django.shortcuts import render

from ontrack.market.tasks.lookup import execute_market_lookup_data_task


def marketdata_index_view(request):
    new_celery_task = execute_market_lookup_data_task.delay()
    return render(request, "market/index.html", {"task_id": new_celery_task.task_id})
