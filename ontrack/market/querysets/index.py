from django.db import models
from django.db.models import Q

from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper


class IndexEndOfDayQuerySet(models.QuerySet):
    def unique_search(self, date, index_id=None, index_symbol=None):
        if index_id is None and index_symbol is None:
            return self.none()

        if date is None:
            return self.none()

        lookups = Q(date=date)

        if index_id is not None:
            lookups = lookups & Q(index_id=index_id)
        else:
            lookups = lookups & Q(index__symbol=index_symbol)

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
