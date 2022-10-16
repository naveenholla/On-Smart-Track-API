from ontrack.utils.base.manager import PullManagerAbstarct

from .queryset import MarketExchangeQuerySet


class MarketExchangePullManager(PullManagerAbstarct):
    def get_queryset(self):
        return MarketExchangeQuerySet(self.model, using=self._db)
