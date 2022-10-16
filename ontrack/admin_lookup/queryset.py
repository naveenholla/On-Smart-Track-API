from django.db import models
from django.db.models import Q


class SettingQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        # lookups = Q(symbol_icontain=query) | Q(name_icontain=query)
        key = str(query["key"]).strip()
        lookups = Q(key=key)
        return self.filter(lookups)
