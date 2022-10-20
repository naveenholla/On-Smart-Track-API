from django.db import models
from django.db.models import Q

from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper


class IndexEndOfDayQuerySet(models.QuerySet):
    def unique_search(self, query=None):
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
