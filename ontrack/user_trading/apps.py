from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserTradingConfig(AppConfig):
    name = "ontrack.user_trading"
    verbose_name = _("User Trading")
