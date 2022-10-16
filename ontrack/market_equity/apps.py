from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EquityConfig(AppConfig):
    name = "ontrack.market_equity"
    verbose_name = _("Market Equity Data")
