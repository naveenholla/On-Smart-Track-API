from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserEventConfig(AppConfig):
    name = "ontrack.user_event"
    verbose_name = _("User Event")
