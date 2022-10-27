from django.db import models

from ontrack.market.managers.equity import (
    EquityDerivativeEndOfDayBackendManager,
    EquityEndOfDayBackendManager,
    EquityLiveDataBackendManager,
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
from ontrack.market.models.lookup import Equity
from ontrack.utils.base.model import BaseModel


class EquityEndOfDay(TradingInformation):
    equity = models.ForeignKey(
        Equity, related_name="eod_data", on_delete=models.CASCADE
    )

    delivery_quantity = models.DecimalField(**numeric_field_values)
    delivery_percentage = models.DecimalField(**numeric_field_values)

    backend = EquityEndOfDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("equity", "date")

    def __str__(self):
        return f"{self.equity.name}-{self.date.strftime('%d/%m/%Y')}"


class EquityEndOfDayCalcutated(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="eod_calculated_data", on_delete=models.CASCADE
    )

    average_quantity_per_trade = models.DecimalField(**numeric_field_values)
    average_volumn = models.DecimalField(**numeric_field_values)
    average_delivery_percentage = models.DecimalField(**numeric_field_values)
    average_open_interest = models.DecimalField(**numeric_field_values)
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    backend = EquityEndOfDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("equity", "date")

    def __str__(self):
        return f"{self.equity.name}-{self.date.strftime('%d/%m/%Y')}"


class EquityInsiderTrade(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="insider_trades", on_delete=models.CASCADE
    )
    category_of_person = models.CharField(max_length=100)
    no_of_shares = models.IntegerField()
    value_of_shares = models.DecimalField(**numeric_field_values)
    mode_of_acquisition = models.CharField(max_length=100)
    pull_date = models.DateField(auto_now=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class EquityPledged(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="equity_pledged", on_delete=models.CASCADE
    )
    total_shares = models.IntegerField()
    total_promoter_holding = models.IntegerField()
    total_public_holding = models.IntegerField()
    total_encumbered_by_promoter = models.IntegerField()
    pull_date = models.DateField(auto_now=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class EquitySast(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="equity_sast", on_delete=models.CASCADE
    )
    total_acquisition = models.IntegerField()
    total_sale = models.IntegerField()
    total_after_acquistion = models.IntegerField()
    pull_date = models.DateField(auto_now=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class EquityDerivativeEndOfDay(DerivativeEndOfDay):
    equity = models.ForeignKey(
        Equity, related_name="derivative_eod_data", on_delete=models.CASCADE
    )

    backend = EquityDerivativeEndOfDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = (
            "equity",
            "date",
            "instrument",
            "expiry_date",
            "strike_price",
            "option_type",
        )

    def __str__(self):
        return (
            f"{self.equity.name}-"
            f"{self.date.strftime('%d/%m/%Y')}-"
            f"{self.instrument}-"
            f"{self.expiry_date.strftime('%d/%m/%Y')}"
        )


class EquityLiveData(EntityLiveData):
    equity = models.ForeignKey(
        Equity, related_name="live_data", on_delete=models.CASCADE
    )

    backend = EquityLiveDataBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.equity.name}-{self.date.strftime('%d/%m/%Y')}"


class EquityLiveOptionChain(EntityLiveOptionChain):
    equity = models.ForeignKey(
        Equity, related_name="live_optionchain", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class EquityLiveFuture(TradableEntity):
    equity = models.ForeignKey(
        Equity, related_name="live_future", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.equity.name}-{self.date.strftime('%d/%m/%Y')}"


class EquityLiveOpenInterest(EntityLiveOpenInterest):
    equity = models.ForeignKey(
        Equity, related_name="live_openInterest", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol
