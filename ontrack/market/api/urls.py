from django.urls import path

from ontrack.market.api.views import lookup

app_name = "market_api"
urlpatterns = [
    path("", view=lookup.api_home, name="api_home"),
]
