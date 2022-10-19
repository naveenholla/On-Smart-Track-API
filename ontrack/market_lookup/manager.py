from ontrack.utils.base.manager import PullManagerAbstarct

from .queryset import (
    EquityIndexQuerySet,
    EquityQuerySet,
    ExchangeQuerySet,
    IndexQuerySet,
)


class ExchangePullManager(PullManagerAbstarct):
    def get_queryset(self):
        return ExchangeQuerySet(self.model, using=self._db)


class EquityPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return EquityQuerySet(self.model, using=self._db)


class IndexPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return IndexQuerySet(self.model, using=self._db)


class EquityIndexPullManager(PullManagerAbstarct):
    def get_queryset(self):
        return EquityIndexQuerySet(self.model, using=self._db)
