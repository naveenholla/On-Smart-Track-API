from ontrack.utils.base.manager import EndOfDayPullManagerAbstract, PullManagerAbstarct

from .queryset import EquityEndOfDayQuerySet, EquityQuerySet


class EquityPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return EquityQuerySet(self.model, using=self._db)


class EquityEndOfDayPullManager(EndOfDayPullManagerAbstract):
    def get_queryset(self):
        return EquityEndOfDayQuerySet(self.model, using=self._db)
