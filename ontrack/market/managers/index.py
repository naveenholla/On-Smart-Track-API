from ontrack.market.querysets.index import (
    IndexDerivativeQuerySet,
    IndexEndOfDayQuerySet,
    IndexLiveDataQuerySet,
    IndexLiveOpenInterestQuerySet,
)
from ontrack.utils.base.manager import EndOfDayBackendManagerAbstract


class IndexEndOfDayBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexEndOfDayQuerySet(self.model, using=self._db)


class IndexDerivativeBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexDerivativeQuerySet(self.model, using=self._db)


class IndexLiveDataBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexLiveDataQuerySet(self.model, using=self._db)


class IndexLiveOpenInterestManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexLiveOpenInterestQuerySet(self.model, using=self._db)
