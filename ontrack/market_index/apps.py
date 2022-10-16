from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IndexConfig(AppConfig):
    name = "ontrack.market_index"
    verbose_name = _("Market Index Data")
