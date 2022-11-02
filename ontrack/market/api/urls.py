from django.urls import path

from ontrack.market.api.views import lookup

app_name = "api_market"
urlpatterns = [
    path("", view=lookup.ExchangeListCreateAPIView.as_view(), name="exchange-list"),
    path("task/execute/", view=lookup.EndOfDayTaskAPIView.as_view(), name="task-eod"),
    path(
        "<str:pk>/", view=lookup.ExchangeDetailAPIView.as_view(), name="exchange-detail"
    ),
]
