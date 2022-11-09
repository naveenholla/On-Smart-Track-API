from django.urls import path

from .api.views.endofday import StockSelectionAPIView

app_name = "market"
urlpatterns = [path("index/", view=StockSelectionAPIView.as_view(), name="index")]
