from django.db.models import Q

from ontrack.market.querysets.base import BaseEntityQuerySet


class ParticipantActivityQuerySet(BaseEntityQuerySet):
    def unique_search(self, date, client_type, instrument, option_type=None):

        if date is None or client_type is None or instrument is None:
            return self.none()

        lookups = (
            Q(date=date)
            & Q(instrument__iexact=instrument)
            & Q(client_type__iexact=client_type)
        )

        if option_type is not None:
            lookups = lookups & Q(option_type__iexact=option_type)

        return self.filter(lookups)


class ParticipantStatsActivityQuerySet(ParticipantActivityQuerySet):
    pass
