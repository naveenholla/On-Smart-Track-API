from ontrack.market.querysets.index import IndexEndOfDayQuerySet
from ontrack.utils.base.manager import EndOfDayPullManagerAbstract


class IndexEndOfDayPullManager(EndOfDayPullManagerAbstract):
    def get_queryset(self):
        return IndexEndOfDayQuerySet(self.model, using=self._db)
