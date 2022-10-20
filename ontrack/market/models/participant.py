from django.db import models

from ontrack.utils.base.enum import ClientType, InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel


class ParticipantActivity(BaseModel):
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    option_type = models.CharField(
        max_length=50, choices=OptionType.choices, null=True, blank=True
    )
    client_type = models.CharField(max_length=50, choices=ClientType.choices)
    buy_amount = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    sell_amount = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    net_amount = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    no_of_contracts = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    change_from_previous_day = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    is_stats = models.BooleanField(default=False)
    pull_date = models.DateField(auto_now=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.instrument
