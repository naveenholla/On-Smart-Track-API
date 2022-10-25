from django.db import models

from ontrack.market.managers.participant import (
    ParticipantActivityBackendManager,
    ParticipantStatsActivityBackendManager,
)
from ontrack.market.models.base import DerivativeEndOfDay, numeric_field_values
from ontrack.utils.base.enum import ClientType, InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel


class ParticipantActivity(BaseModel):
    client_type = models.CharField(max_length=50, choices=ClientType.choices)
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    option_type = models.CharField(
        max_length=50, choices=OptionType.choices, null=True, blank=True
    )

    buy_amount = models.DecimalField(**numeric_field_values)
    sell_amount = models.DecimalField(**numeric_field_values)
    net_amount = models.DecimalField(**numeric_field_values)
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    backend = ParticipantActivityBackendManager()

    class Meta(BaseModel.Meta, DerivativeEndOfDay.Meta):
        ordering = ["-created_at"]
        unique_together = ("client_type", "date", "instrument", "option_type")

    def __str__(self):
        return (
            f"{self.client_type}-"
            f"{self.date.strftime('%d/%m/%Y')}-"
            f"{self.instrument}-"
            f"{self.option_type}"
        )


class ParticipantStatsActivity(BaseModel):
    client_type = models.CharField(max_length=50, choices=ClientType.choices)
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)

    no_of_contracts_bought = models.DecimalField(**numeric_field_values)
    value_of_contracts_bought = models.DecimalField(**numeric_field_values)
    no_of_contracts_sold = models.DecimalField(**numeric_field_values)
    value_of_contracts_sold = models.DecimalField(**numeric_field_values)
    open_interest = models.DecimalField(**numeric_field_values)
    value_of_open_interest = models.DecimalField(**numeric_field_values)

    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    backend = ParticipantStatsActivityBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("client_type", "date", "instrument")

    def __str__(self):
        return (
            f"{self.client_type}-"
            f"{self.date.strftime('%d/%m/%Y')}-"
            f"{self.instrument}-"
        )
