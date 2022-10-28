from ontrack.market.querysets.base import EntityDataQuerySet, EntityDerivativeQuerySet


class IndexEndOfDayQuerySet(EntityDataQuerySet):
    pass


class IndexDerivativeQuerySet(EntityDerivativeQuerySet):
    pass


class IndexLiveDataQuerySet(EntityDataQuerySet):
    pass


class IndexLiveOpenInterestQuerySet(EntityDataQuerySet):
    pass
