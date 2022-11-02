from django.urls import path

from ontrack.market.api.views import lookup

app_name = "api_market"
urlpatterns = [
    path("", view=lookup.ExchangeListCreateAPIView.as_view(), name="exchange-list"),
    path(
        "task/initial/data/",
        view=lookup.InitialDataTaskAPIView.as_view(),
        name="task-initial-data",
    ),
    path(
        "task/holidays/",
        view=lookup.HolidaysLookupDataTaskAPIView.as_view(),
        name="task-market-holidays",
    ),
    path(
        "task/lookup/",
        view=lookup.MarketLookupDataTaskAPIView.as_view(),
        name="task-market-lookup",
    ),
    path(
        "<str:pk>/", view=lookup.ExchangeDetailAPIView.as_view(), name="exchange-detail"
    ),
]
