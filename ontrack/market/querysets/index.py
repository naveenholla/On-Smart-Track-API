from django.db import models
from django.db.models import Q

from ontrack.utils.base.enum import InstrumentType
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


class IndexDerivativeEndOfDayQuerySet(models.QuerySet):
    def unique_search(
        self,
        date,
        index_id=None,
        index_symbol=None,
        instrument=InstrumentType.FUTIDX,
        expiry_date=None,
        strike_price=None,
        option_type=None,
    ):

        if index_id is None and index_symbol is None:
            return self.none()

        if date is None or expiry_date is None:
            return self.none()

        lookups = Q(date=date)

        if index_id is not None:
            lookups = lookups & Q(index_id=index_id)
        else:
            lookups = lookups & Q(index__symbol=index_symbol)

        lookups = lookups & Q(instrument=instrument) & Q(expiry_date=expiry_date)

        if strike_price is not None and option_type is not None:
            lookups = (
                lookups & Q(strike_price=strike_price) & Q(option_type=option_type)
            )

        return self.filter(lookups)

    def get_records_after_date(self, query):
        if query is None:
            return self.none()

        date = query["date"]
        average_date = DateTimeHelper.get_past_date(
            date, days=Configurations.get_default_values_config()["average_days_count"]
        )
        lookups = (
            Q(date__gte=average_date)
            & Q(date__lt=query["date"])
            & Q(index__symbol=query["symbol"])
        )
        return self.filter(lookups)

    def search_old_records(self):
        threshold = DateTimeHelper.get_past_date(
            days=Configurations.get_default_values_config()[
                "days_for_delete_index_eod_data"
            ]
        )
        return self.filter(date__lt=threshold)

    def search_records_after_date(self, date):
        return self.filter(date__gte=date)


class IndexLiveDataQuerySet(models.QuerySet):
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
