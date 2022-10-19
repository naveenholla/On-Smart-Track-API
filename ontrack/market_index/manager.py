from ontrack.utils.base.manager import EndOfDayPullManagerAbstract

from .queryset import IndexEndOfDayQuerySet


class IndexEndOfDayPullManager(EndOfDayPullManagerAbstract):
    def get_queryset(self):
        return IndexEndOfDayQuerySet(self.model, using=self._db)
