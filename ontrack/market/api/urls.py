from django.urls import path

from ontrack.market.api.views import endofday, equity, lookup

app_name = "api_market"
urlpatterns = [
    path(
        "exchange/",
        view=lookup.ExchangeListCreateAPIView.as_view(),
        name="exchange-list",
    ),
    path(
        "exchange/<str:pk>/",
        view=lookup.ExchangeDetailAPIView.as_view(),
        name="exchange-detail",
    ),
    path(
        "equity/",
        view=equity.EquityListCreateAPIView.as_view(),
        name="equity-list",
    ),
    path(
        "equity/<str:slug__iexact>/",
        view=equity.EquityDetailAPIView.as_view(),
        name="equity-detail",
    ),
    path(
        "task/eod/equity/",
        view=endofday.EquityEndOfDayDataTaskAPIView.as_view(),
        name="task-eod-equity",
    ),
    path(
        "task/lookup/initial/",
        view=lookup.InitialDataTaskAPIView.as_view(),
        name="task-lookup-initial",
    ),
    path(
        "task/lookup/holidays/",
        view=lookup.HolidaysLookupDataTaskAPIView.as_view(),
        name="task-lookup-holidays",
    ),
    path(
        "task/lookup/equity/",
        view=lookup.MarketLookupDataTaskAPIView.as_view(),
        name="task-lookup-equity",
    ),
]
