from django.contrib.auth import get_user_model
from django.shortcuts import render

# from ontrack.market.tasks.lookup import
# create_intial_market_lookup_data_task,
# create_lookup_data_files, pull_equity_lookup_data

# from ontrack.market.tasks.equity import (
#     pull_equity_eod_data,
#     pull_indices_eod_data,
# )

# from ontrack.market.tasks.index import (
#     pull_indices_eod_data,
# )

User = get_user_model()


def marketdata_index_view(request, id):
    # if id == 1:
    #     task = create_intial_market_lookup_data_task.delay()

    # if id == 2:
    #     task = create_lookup_data_files.delay()

    # if id == 3:
    #     task = pull_equity_lookup_data.delay()

    # if id == 4:
    #     task = pull_equity_eod_data.delay()

    # if id == 5:
    #     task = pull_indices_eod_data.delay()

    return render(request, "marketdata/index.html")  # , {"task_id": task.task_id})
