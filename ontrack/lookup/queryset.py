from django.db.models import Q

from ontrack.market.querysets.base import BaseQuerySet


class SettingQuerySet(BaseQuerySet):
    def unique_search(self, query=None):
        if query is None:
            return self.none()

        # lookups = Q(symbol_icontain=query) | Q(name_icontain=query)
        key = str(query["key"]).strip()
        lookups = Q(key=key)
        return self.filter(lookups)


class TaskQuerySet(BaseQuerySet):
    def unique_search(self, task_id=None):
        if task_id is None:
            return self.none()

        lookups = Q(task_id=task_id)
        return self.filter(lookups)
