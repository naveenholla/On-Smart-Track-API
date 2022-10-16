from django.db import models
from django.db.models import Q


class MarketExchangeQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        name = str(query["name"]).strip()
        lookups = Q(name=name)

        if "exchange_name" in query:
            lookups = lookups | Q(name=query["exchange_name"])

        return self.filter(lookups)
