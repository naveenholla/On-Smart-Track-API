from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserAccountConfig(AppConfig):
    name = "ontrack.user_account"
    verbose_name = _("User Account")
