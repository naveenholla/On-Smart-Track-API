from ontrack.market.querysets.lookup import (
    EquityIndexQuerySet,
    EquityQuerySet,
    ExchangeQuerySet,
    IndexQuerySet,
    MarketDayCategoryQuerySet,
    MarketDayQuerySet,
    MarketDayTypeQuerySet,
)
from ontrack.utils.base.manager import BackendManagerAbstarct


class ExchangeBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return ExchangeQuerySet(self.model, using=self._db)


class EquityBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return EquityQuerySet(self.model, using=self._db)


class IndexBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return IndexQuerySet(self.model, using=self._db)


class EquityIndexBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return EquityIndexQuerySet(self.model, using=self._db)


class MarketDayTypeBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return MarketDayTypeQuerySet(self.model, using=self._db)


class MarketDayCategoryBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return MarketDayCategoryQuerySet(self.model, using=self._db)


class MarketDayBackendManager(BackendManagerAbstarct):
    def get_queryset(self):
        return MarketDayQuerySet(self.model, using=self._db)
