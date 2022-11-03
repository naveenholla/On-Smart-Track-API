from django.db import models


class BackendManagerAbstarct(models.Manager):
    def unique_entity(self, uid=None):
        return self.get_queryset().unique_entity(uid)

    def unique_search(self, symbol=None, name=None):
        return self.get_queryset().unique_search(symbol=symbol, name=name)

    def bulk_create_or_update(
        self, records_to_create, records_to_update, fields_to_update
    ):
        self.bulk_create(records_to_create, batch_size=1000)
        self.bulk_update(records_to_update, fields_to_update, batch_size=1000)

    def get_records_after_date(self, query):
        return self.get_queryset().get_records_after_date(query=query)

    def delete_old_records(self, days_count):
        self.get_queryset().search_old_records(days_count).delete()

    def delete_records_after_date(self, date):
        self.get_queryset().search_records_after_date(date).delete()


class EndOfDayBackendManagerAbstract(BackendManagerAbstarct):
    pass
