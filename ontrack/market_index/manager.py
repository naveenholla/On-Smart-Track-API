from ontrack.utils.base.manager import EndOfDayPullManagerAbstract, PullManagerAbstarct

from .queryset import EquityIndexQuerySet, IndexEndOfDayQuerySet, IndexQuerySet


class IndexPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return IndexQuerySet(self.model, using=self._db)


class EquityIndexPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return EquityIndexQuerySet(self.model, using=self._db)


class IndexEndOfDayPullManager(EndOfDayPullManagerAbstract):
    def get_queryset(self):
        return IndexEndOfDayQuerySet(self.model, using=self._db)
