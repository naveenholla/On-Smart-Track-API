from django.urls import path

from ontrack.users.views.accounts import demat_account_list_view, demat_login_view
from ontrack.users.views.user import (
    user_detail_view,
    user_redirect_view,
    user_update_view,
)

app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("demat/", view=demat_account_list_view, name="demat"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]

htmx_urlpatterns = [
    path("demat/login/<str:id>/", view=demat_login_view, name="demat-login"),
]

urlpatterns += htmx_urlpatterns
