from django.urls import path

from .views.views import marketdata_index_view

app_name = "market"
urlpatterns = [path("index/<int:id>", view=marketdata_index_view, name="index")]
