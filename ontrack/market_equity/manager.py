from ontrack.utils.base.manager import EndOfDayPullManagerAbstract

from .queryset import EquityEndOfDayQuerySet


class EquityEndOfDayPullManager(EndOfDayPullManagerAbstract):
    def get_queryset(self):
        return EquityEndOfDayQuerySet(self.model, using=self._db)
