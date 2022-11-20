from django.urls import path

from ontrack.market.consumers import TaskProgressConsumer
from ontrack.market.views.tasks import task_execution_view

from .api.views.endofday import StockSelectionAPIView

app_name = "market"
urlpatterns = [
    path("index/", view=StockSelectionAPIView.as_view(), name="index"),
    path("task/<str:task_name>/", view=task_execution_view, name="task-execution"),
]


websocket_urlpatterns = [
    path("ws/task/<str:task_id>/", TaskProgressConsumer.as_asgi()),
]
