from django.db import models


class BackendManagerAbstarct(models.Manager):
    def unique_search(self, symbol=None, name=None):
        return self.get_queryset().unique_search(symbol=symbol, name=name)

    def bulk_create_or_update(
        self, records_to_create, records_to_update, fields_to_update
    ):
        self.bulk_create(records_to_create, batch_size=1000)
        self.bulk_update(records_to_update, fields_to_update, batch_size=1000)

    def delete_old_records(self):
        self.get_queryset().search_old_records().delete()


class EndOfDayBackendManagerAbstract(BackendManagerAbstarct):
    def get_records_after_date(self, query):
        return self.get_queryset().get_records_after_date(query=query)

    def delete_records_after_date(self, date):
        self.get_queryset().search_records_after_date(date).delete()


class CommonLogic:
    def create_or_update(self, data, entityType):
        if data is None or len(data) == 0:
            return

        records_to_create = [x for x in data if x["id"] is None]
        records_to_update = [x for x in data if x["id"] is not None]
        new_records = [entityType(**values) for values in records_to_create]
        existing_records = [entityType(**values) for values in records_to_update]

        record_keys = list(data[0].keys())
        record_keys.remove("id")
        entityType.backend.bulk_create_or_update(
            new_records, existing_records, record_keys
        )
