from ontrack.market.querysets.equity import (
    EquityDerivativeQuerySet,
    EquityEndOfDayQuerySet,
    EquityLiveDataQuerySet,
    EquityLiveOpenInterestQuerySet,
)
from ontrack.utils.base.manager import EndOfDayBackendManagerAbstract


class EquityEndOfDayBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return EquityEndOfDayQuerySet(self.model, using=self._db)


class EquityDerivativeBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return EquityDerivativeQuerySet(self.model, using=self._db)


class EquityLiveDataBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return EquityLiveDataQuerySet(self.model, using=self._db)


class EquityLiveOpenInterestManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return EquityLiveOpenInterestQuerySet(self.model, using=self._db)
