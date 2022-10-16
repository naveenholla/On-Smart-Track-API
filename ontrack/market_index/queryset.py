from django.db import models
from django.db.models import Q

from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper


class IndexQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        lookups = Q(name=query["name"])

        if "symbol" in query:
            lookups = (
                lookups | Q(symbol=query["symbol"]) | Q(chart_symbol=query["symbol"])
            )

        if "index_symbol" in query:
            lookups = (
                lookups
                | Q(symbol=query["index_symbol"])
                | Q(chart_symbol=query["index_symbol"])
            )

        return self.filter(lookups)


class EquityIndexQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        lookups = Q(index__symbol=query["index_symbol"]) & Q(
            equity__symbol=query["symbol"]
        )
        return self.filter(lookups)

    def search_old_records(self):
        threshold = DateTimeHelper.get_past_date(
            days=Configurations.get_default_values_config()[
                "days_for_delete_lookup_data"
            ]
        )
        return self.filter(last_update_date__lt=threshold)


class IndexEndOfDayQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        lookups = Q(date=query["date"]) & Q(index__name=query["name"])
        return self.filter(lookups)

    def search_old_records(self):
        threshold = DateTimeHelper.get_past_date(
            days=Configurations.get_default_values_config()[
                "days_for_delete_indices_eod_data"
            ]
        )
        return self.filter(date__lt=threshold)

    def search_records_after_date(self, date):
        return self.filter(date__gte=date)
