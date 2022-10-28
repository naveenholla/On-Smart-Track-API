from ontrack.market.querysets.base import EntityDataQuerySet, EntityDerivativeQuerySet


class EquityEndOfDayQuerySet(EntityDataQuerySet):
    pass


class EquityDerivativeQuerySet(EntityDerivativeQuerySet):
    pass


class EquityLiveDataQuerySet(EntityDataQuerySet):
    pass


class EquityLiveOpenInterestQuerySet(EntityDataQuerySet):
    pass
