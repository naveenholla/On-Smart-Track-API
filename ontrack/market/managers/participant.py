from ontrack.market.querysets.participant import (
    ParticipantActivityQuerySet,
    ParticipantStatsActivityQuerySet,
)
from ontrack.utils.base.manager import EndOfDayBackendManagerAbstract


class ParticipantActivityBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return ParticipantActivityQuerySet(self.model, using=self._db)


class ParticipantStatsActivityBackendManager(EndOfDayBackendManagerAbstract):
    def get_queryset(self):
        return ParticipantStatsActivityQuerySet(self.model, using=self._db)
