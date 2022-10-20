from django.db import models

from ontrack.market_lookup.models.lookup import Index
from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel

from .manager import IndexEndOfDayPullManager


class DerivativeEndOfDay(BaseModel):
    index = models.ForeignKey(
        Index, related_name="derivative_eod_datas", on_delete=models.CASCADE
    )
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    expiry_date = models.DateField()
    strike_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    option_type = models.CharField(max_length=50, choices=OptionType.choices)
    open_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    high_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    low_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    close_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    settle_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    no_of_contracts = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    value_of_contracts = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    change_in_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pull_date = models.DateField(auto_now=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class IndexEndOfDay(BaseModel):
    index = models.ForeignKey(
        Index, related_name="index_eod_datas", on_delete=models.CASCADE
    )
    prev_close = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    high_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    low_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    close_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    point_changed = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    percentage_changed = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    traded_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    turn_overs_in_cr = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    index_pe = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    index_pb = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    index_div_yield = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    datapull_manager = IndexEndOfDayPullManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class LiveIndexData(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    prev_close = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    high_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    low_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    last_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    point_changed = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    percentage_changed = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    traded_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    traded_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    year_high = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    year_low = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    near_week_high = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    near_week_low = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    one_week_ago = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    one_month_ago = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    one_year_ago = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    declines = models.IntegerField(null=True, blank=True)
    advances = models.IntegerField(null=True, blank=True)
    unchanged = models.IntegerField(null=True, blank=True)
    lastest_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    previous_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    change_in_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    average_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    volume_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    underlying_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class LiveOptionChain(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    pe_strike_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_expiry_date = models.DateField()
    pe_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_change_in_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_total_traded_volume = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_implied_volatility = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_last_traded_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_change = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_total_buy_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_total_sell_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_bid_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_bid_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_ask_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_ask_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    pe_underlying_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_strike_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_expiry_date = models.DateField()
    ce_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_change_in_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_total_traded_volume = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_implied_volatility = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_last_traded_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_change = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_total_buy_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_total_sell_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_bid_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_bid_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_ask_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_ask_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ce_underlying_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )

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
    strike_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    last_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    change = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    change_percentage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    Volume = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    total_turn_over = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    value = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    premium_turn_over = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    underlying_value = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    no_of_traded = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class LiveIndexDerivative(BaseModel):
    symbol = models.CharField(max_length=100)
    date = models.DateTimeField()
    month = models.CharField(max_length=100)
    prev_close = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    high_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    low_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    last_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    point_changed = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    percentage_changed = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    is_future = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol
