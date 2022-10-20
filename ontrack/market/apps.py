from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LookupConfig(AppConfig):
    name = "ontrack.market"
    verbose_name = _("Market Data")
