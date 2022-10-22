from ontrack.market.querysets.equity import EquityEndOfDayQuerySet
from ontrack.utils.base.manager import EndOfDayBackendManagerAbstract


class EquityEndOfDayBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return EquityEndOfDayQuerySet(self.model, using=self._db)
