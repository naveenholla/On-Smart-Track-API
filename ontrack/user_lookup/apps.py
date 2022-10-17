from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UserLookupConfig(AppConfig):
    name = "ontrack.user_lookup"
    verbose_name = _("User Lookup")
