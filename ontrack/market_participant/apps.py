from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ParticipantConfig(AppConfig):
    name = "ontrack.market_participant"
    verbose_name = _("Market Participant Data")
