from django.db import models

from ontrack.market.managers.index import IndexEndOfDayBackendManager
from ontrack.market.models.base import TradableEntityEndOfDayData, numeric_field_values
from ontrack.market.models.lookup import Index
from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel


class IndexEndOfDay(TradableEntityEndOfDayData):
    index = models.ForeignKey(Index, related_name="eod_data", on_delete=models.CASCADE)

    index_pe = models.DecimalField(**numeric_field_values)
    index_pb = models.DecimalField(**numeric_field_values)
    index_div_yield = models.DecimalField(**numeric_field_values)

    backend = IndexEndOfDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("index", "date")

    def __str__(self):
        return self.equity.name


class IndexDerivativeEndOfDay(BaseModel):
    index = models.ForeignKey(
        Index, related_name="derivative_eod_data", on_delete=models.CASCADE
    )
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    expiry_date = models.DateField()
    strike_price = models.DecimalField(**numeric_field_values)
    option_type = models.CharField(max_length=50, choices=OptionType.choices)
    open_price = models.DecimalField(**numeric_field_values)
    high_price = models.DecimalField(**numeric_field_values)
    low_price = models.DecimalField(**numeric_field_values)
    close_price = models.DecimalField(**numeric_field_values)
    settle_price = models.DecimalField(**numeric_field_values)
    no_of_contracts = models.DecimalField(**numeric_field_values)
    value_of_contracts = models.DecimalField(**numeric_field_values)
    open_interest = models.DecimalField(**numeric_field_values)
    change_in_open_interest = models.DecimalField(**numeric_field_values)
    pull_date = models.DateField(auto_now=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class LiveIndexData(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    prev_close = models.DecimalField(**numeric_field_values)
    open_price = models.DecimalField(**numeric_field_values)
    high_price = models.DecimalField(**numeric_field_values)
    low_price = models.DecimalField(**numeric_field_values)
    last_price = models.DecimalField(**numeric_field_values)
    point_changed = models.DecimalField(**numeric_field_values)
    percentage_changed = models.DecimalField(**numeric_field_values)
    traded_quantity = models.DecimalField(**numeric_field_values)
    traded_value = models.DecimalField(**numeric_field_values)
    year_high = models.DecimalField(**numeric_field_values)
    year_low = models.DecimalField(**numeric_field_values)
    near_week_high = models.DecimalField(**numeric_field_values)
    near_week_low = models.DecimalField(**numeric_field_values)
    one_week_ago = models.DecimalField(**numeric_field_values)
    one_month_ago = models.DecimalField(**numeric_field_values)
    one_year_ago = models.DecimalField(**numeric_field_values)
    declines = models.IntegerField(null=True, blank=True)
    advances = models.IntegerField(null=True, blank=True)
    unchanged = models.IntegerField(null=True, blank=True)
    lastest_open_interest = models.DecimalField(**numeric_field_values)
    previous_open_interest = models.DecimalField(**numeric_field_values)
    change_in_open_interest = models.DecimalField(**numeric_field_values)
    average_open_interest = models.DecimalField(**numeric_field_values)
    volume_open_interest = models.DecimalField(**numeric_field_values)
    underlying_value = models.DecimalField(**numeric_field_values)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class LiveIndexOptionChain(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    pe_strike_price = models.DecimalField(**numeric_field_values)
    pe_expiry_date = models.DateField()
    pe_open_interest = models.DecimalField(**numeric_field_values)
    pe_change_in_open_interest = models.DecimalField(**numeric_field_values)
    pe_total_traded_volume = models.DecimalField(**numeric_field_values)
    pe_implied_volatility = models.DecimalField(**numeric_field_values)
    pe_last_traded_price = models.DecimalField(**numeric_field_values)
    pe_change = models.DecimalField(**numeric_field_values)
    pe_total_buy_quantity = models.DecimalField(**numeric_field_values)
    pe_total_sell_quantity = models.DecimalField(**numeric_field_values)
    pe_bid_quantity = models.DecimalField(**numeric_field_values)
    pe_bid_price = models.DecimalField(**numeric_field_values)
    pe_ask_quantity = models.DecimalField(**numeric_field_values)
    pe_ask_price = models.DecimalField(**numeric_field_values)
    pe_underlying_value = models.DecimalField(**numeric_field_values)
    ce_strike_price = models.DecimalField(**numeric_field_values)
    ce_expiry_date = models.DateField()
    ce_open_interest = models.DecimalField(**numeric_field_values)
    ce_change_in_open_interest = models.DecimalField(**numeric_field_values)
    ce_total_traded_volume = models.DecimalField(**numeric_field_values)
    ce_implied_volatility = models.DecimalField(**numeric_field_values)
    ce_last_traded_price = models.DecimalField(**numeric_field_values)
    ce_change = models.DecimalField(**numeric_field_values)
    ce_total_buy_quantity = models.DecimalField(**numeric_field_values)
    ce_total_sell_quantity = models.DecimalField(**numeric_field_values)
    ce_bid_quantity = models.DecimalField(**numeric_field_values)
    ce_bid_price = models.DecimalField(**numeric_field_values)
    ce_ask_quantity = models.DecimalField(**numeric_field_values)
    ce_ask_price = models.DecimalField(**numeric_field_values)
    ce_underlying_value = models.DecimalField(**numeric_field_values)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


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


class LiveIndexDerivative(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    month = models.CharField(max_length=100)
    prev_close = models.DecimalField(**numeric_field_values)
    open_price = models.DecimalField(**numeric_field_values)
    high_price = models.DecimalField(**numeric_field_values)
    low_price = models.DecimalField(**numeric_field_values)
    last_price = models.DecimalField(**numeric_field_values)
    point_changed = models.DecimalField(**numeric_field_values)
    percentage_changed = models.DecimalField(**numeric_field_values)
    is_future = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol
