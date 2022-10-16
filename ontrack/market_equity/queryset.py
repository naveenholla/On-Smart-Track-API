from django.db import models
from django.db.models import Q

from ontrack.utils.config import Configurations
from ontrack.utils.datetime import DateTimeHelper


class EquityQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        # lookups = Q(symbol_icontain=query) | Q(name_icontain=query)
        symbol = str(query["symbol"]).strip()
        lookups = Q(symbol=symbol)
        return self.filter(lookups)


class EquityEndOfDayQuerySet(models.QuerySet):
    def search_unique_record(self, query=None):
        if query is None:
            return self.none()

        lookups = Q(date=query["date"]) & Q(equity__symbol=query["symbol"])
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
            & Q(equity__symbol=query["symbol"])
        )
        return self.filter(lookups)

    def search_old_records(self):
        threshold = DateTimeHelper.get_past_date(
            days=Configurations.get_default_values_config()[
                "days_for_delete_equity_eod_data"
            ]
        )
        return self.filter(date__lt=threshold)

    def search_records_after_date(self, date):
        return self.filter(date__gte=date)
