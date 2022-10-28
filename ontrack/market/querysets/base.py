from django.db import models
from django.db.models import Q

from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper


class EntityQuerySet(models.QuerySet):
    def unique_search(self, symbol=None, name=None):
        if symbol is None and name is None:
            return self.none()

        if symbol is not None:
            lookups = Q(symbol__iexact=symbol)

        if name is not None:
            lookups = Q(name__iexact=name)

        return self.filter(lookups)


class EntityDataQuerySet(models.QuerySet):
    def unique_search(self, date, entity_id=None, entity_symbol=None):
        if entity_id is None and entity_symbol is None:
            return self.none()

        if date is None:
            return self.none()

        lookups = Q(date=date)

        if entity_id is not None:
            lookups = lookups & Q(entity_id=entity_id)
        else:
            lookups = lookups & Q(entity__symbol=entity_symbol)

        return self.filter(lookups)

    def get_records_after_date(self, query, days_count_key):
        if query is None:
            return self.none()

        days_count = Configurations.get_default_values_config()[days_count_key]
        date = query["date"]
        average_date = DateTimeHelper.get_past_date(date, days=days_count)
        lookups = (
            Q(date__gte=average_date)
            & Q(date__lt=query["date"])
            & Q(entity__symbol=query["symbol"])
        )
        return self.filter(lookups)

    def search_old_records(self, days_for_delete_key):
        days_count = Configurations.get_default_values_config()[days_for_delete_key]
        threshold = DateTimeHelper.get_past_date(days=days_count)
        return self.filter(date__lt=threshold)

    def search_records_after_date(self, date):
        return self.filter(date__gte=date)


class EntityDerivativeQuerySet(EntityDataQuerySet):
    def unique_search(
        self,
        date,
        instrument,
        expiry_date,
        entity_id=None,
        entity_symbol=None,
        strike_price=None,
        option_type=None,
    ):

        if entity_id is None and entity_symbol is None:
            return self.none()

        lookups = Q(date=date)

        if entity_id is not None:
            lookups = lookups & Q(entity_id=entity_id)
        else:
            lookups = lookups & Q(entity__symbol=entity_symbol)

        lookups = lookups & Q(instrument=instrument) & Q(expiry_date=expiry_date)

        if strike_price is not None and option_type is not None:
            lookups = (
                lookups & Q(strike_price=strike_price) & Q(option_type=option_type)
            )

        return self.filter(lookups)
