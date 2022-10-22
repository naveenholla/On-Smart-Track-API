from ontrack.market.querysets.index import IndexEndOfDayQuerySet
from ontrack.utils.base.manager import EndOfDayBackendManagerAbstract


class IndexEndOfDayBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return IndexEndOfDayQuerySet(self.model, using=self._db)
