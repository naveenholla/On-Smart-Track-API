from django.urls import path

from ontrack.market.consumers import TaskProgressConsumer
from ontrack.market.views.views import marketdata_index_view

from .api.views.endofday import StockSelectionAPIView

app_name = "market"
urlpatterns = [
    path("index/", view=StockSelectionAPIView.as_view(), name="index"),
    path("index2/", view=marketdata_index_view, name="index2"),
]


websocket_urlpatterns = [
    path("ws/task/<str:task_id>/", TaskProgressConsumer.as_asgi()),
]
