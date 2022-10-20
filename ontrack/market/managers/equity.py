from ontrack.market.querysets.equity import EquityEndOfDayQuerySet
from ontrack.utils.base.manager import EndOfDayPullManagerAbstract


class EquityEndOfDayPullManager(EndOfDayPullManagerAbstract):
    def get_queryset(self):
        return EquityEndOfDayQuerySet(self.model, using=self._db)
