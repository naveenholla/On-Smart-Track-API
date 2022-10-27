from django.db import models

from ontrack.market.managers.index import (
    IndexDerivativeEndOfDayBackendManager,
    IndexEndOfDayBackendManager,
    IndexLiveDataBackendManager,
    IndexLiveOpenInterestManager,
)
from ontrack.market.models.base import (
    DerivativeEndOfDay,
    EntityLiveData,
    EntityLiveOpenInterest,
    EntityLiveOptionChain,
    TradableEntity,
    TradingInformation,
    numeric_field_values,
)
from ontrack.market.models.lookup import Index
from ontrack.utils.base.enum import OptionType
from ontrack.utils.base.model import BaseModel


class IndexEndOfDay(TradingInformation):
    index = models.ForeignKey(Index, related_name="eod_data", on_delete=models.CASCADE)

    index_pe = models.DecimalField(**numeric_field_values)
    index_pb = models.DecimalField(**numeric_field_values)
    index_div_yield = models.DecimalField(**numeric_field_values)

    backend = IndexEndOfDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("index", "date")

    def __str__(self):
        return f"{self.index.name}-{self.date.strftime('%d/%m/%Y')}"


class IndexDerivativeEndOfDay(DerivativeEndOfDay):
    index = models.ForeignKey(
        Index, related_name="derivative_eod_data", on_delete=models.CASCADE
    )

    backend = IndexDerivativeEndOfDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = (
            "index",
            "date",
            "instrument",
            "expiry_date",
            "strike_price",
            "option_type",
        )

    def __str__(self):
        return (
            f"{self.index.name}-"
            f"{self.date.strftime('%d/%m/%Y')}-"
            f"{self.instrument}-"
            f"{self.expiry_date.strftime('%d/%m/%Y')}"
        )


class IndexLiveData(EntityLiveData):
    index = models.ForeignKey(Index, related_name="live_data", on_delete=models.CASCADE)

    one_week_ago = models.DecimalField(**numeric_field_values)
    one_month_ago = models.DecimalField(**numeric_field_values)
    declines = models.IntegerField(null=True, blank=True)
    advances = models.IntegerField(null=True, blank=True)
    unchanged = models.IntegerField(null=True, blank=True)

    backend = IndexLiveDataBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = (
            "index",
            "date",
        )

    def __str__(self):
        return f"{self.index.name}-{self.date.strftime('%d/%m/%Y')}"


class IndexLiveOptionChain(EntityLiveOptionChain):
    index = models.ForeignKey(
        Index, related_name="live_optionchain", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class IndexLiveFuture(TradableEntity):
    index = models.ForeignKey(
        Index, related_name="live_future", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.index.name}-{self.date.strftime('%d/%m/%Y')}"


class IndexLiveOpenInterest(EntityLiveOpenInterest):
    index = models.ForeignKey(
        Index, related_name="live_openInterest", on_delete=models.CASCADE
    )

    backend = IndexLiveOpenInterestManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = (
            "index",
            "date",
        )

    def __str__(self):
        return f"{self.index.name}-{self.date.strftime('%d/%m/%Y')}"


class MajorIndexData(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    contract_name = models.CharField(max_length=100)
    expiry_date = models.DateField()
    option_type = models.CharField(max_length=50, choices=OptionType.choices)
    strike_price = models.DecimalField(**numeric_field_values)
    last_price = models.DecimalField(**numeric_field_values)
    change = models.DecimalField(**numeric_field_values)
    change_percentage = models.DecimalField(**numeric_field_values)
    Volume = models.DecimalField(**numeric_field_values)
    total_turn_over = models.DecimalField(**numeric_field_values)
    value = models.DecimalField(**numeric_field_values)
    premium_turn_over = models.DecimalField(**numeric_field_values)
    underlying_value = models.DecimalField(**numeric_field_values)
    open_interest = models.DecimalField(**numeric_field_values)
    no_of_traded = models.DecimalField(**numeric_field_values)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol
