from django.urls import path

from ontrack.users.api.views.accounts import DematAccountAPIView

app_name = "api_users"
urlpatterns = [
    path(
        "demat/",
        view=DematAccountAPIView.as_view(),
        name="demat-account-list",
    ),
]
