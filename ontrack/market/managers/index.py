from ontrack.market.querysets.index import (
    IndexDerivativeEndOfDayQuerySet,
    IndexEndOfDayQuerySet,
    IndexLiveDataQuerySet,
    IndexLiveOpenInterestQuerySet,
)
from ontrack.utils.base.manager import EndOfDayBackendManagerAbstract


class IndexEndOfDayBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexEndOfDayQuerySet(self.model, using=self._db)


class IndexDerivativeEndOfDayBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexDerivativeEndOfDayQuerySet(self.model, using=self._db)


class IndexLiveDataBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexLiveDataQuerySet(self.model, using=self._db)


class IndexLiveOpenInterestManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexLiveOpenInterestQuerySet(self.model, using=self._db)
