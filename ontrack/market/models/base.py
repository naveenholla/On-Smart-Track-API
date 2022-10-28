from django.db import models

from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel

numeric_field_values = {
    "max_digits": 18,
    "decimal_places": 4,
    "null": True,
    "blank": True,
}


class MarketEntity(BaseModel):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200, unique=True)
    chart_symbol = models.CharField(max_length=200, unique=True, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)
    lot_size = models.IntegerField(default=0, null=True, blank=True)
    strike_difference = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class TradableEntity(BaseModel):
    prev_close = models.DecimalField(**numeric_field_values)
    open_price = models.DecimalField(**numeric_field_values)
    high_price = models.DecimalField(**numeric_field_values)
    low_price = models.DecimalField(**numeric_field_values)
    last_price = models.DecimalField(**numeric_field_values)
    close_price = models.DecimalField(**numeric_field_values)
    avg_price = models.DecimalField(**numeric_field_values)
    point_changed = models.DecimalField(**numeric_field_values)
    percentage_changed = models.DecimalField(**numeric_field_values)

    class Meta:
        abstract = True


class TradingInformation(TradableEntity):
    traded_quantity = models.DecimalField(**numeric_field_values)
    traded_value = models.DecimalField(**numeric_field_values)
    number_of_trades = models.DecimalField(**numeric_field_values)
    quantity_per_trade = models.DecimalField(**numeric_field_values)
    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DerivativeEndOfDay(TradableEntity):
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    expiry_date = models.DateField()
    strike_price = models.DecimalField(**numeric_field_values)
    option_type = models.CharField(
        max_length=50, choices=OptionType.choices, null=True, blank=True
    )
    no_of_contracts = models.DecimalField(**numeric_field_values)
    value_of_contracts = models.DecimalField(**numeric_field_values)
    open_interest = models.DecimalField(**numeric_field_values)
    change_in_open_interest = models.DecimalField(**numeric_field_values)
    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LiveDerivativeData(TradableEntity):
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    contract = models.CharField(max_length=200)
    identifier = models.CharField(max_length=200)
    list_type = models.CharField(max_length=200, null=True, blank=True)
    expiry_date = models.DateField()
    strike_price = models.DecimalField(**numeric_field_values)
    option_type = models.CharField(
        max_length=50, choices=OptionType.choices, null=True, blank=True
    )
    last_price = models.DecimalField(**numeric_field_values)
    point_changed = models.DecimalField(**numeric_field_values)
    percentage_changed = models.DecimalField(**numeric_field_values)
    volumn = models.DecimalField(**numeric_field_values)
    open_interest = models.DecimalField(**numeric_field_values)
    change_in_open_interest = models.DecimalField(**numeric_field_values)
    no_of_trades = models.DecimalField(**numeric_field_values)

    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EntityLiveData(TradingInformation):
    year_high = models.DecimalField(**numeric_field_values)
    year_low = models.DecimalField(**numeric_field_values)
    near_week_high = models.DecimalField(**numeric_field_values)
    near_week_low = models.DecimalField(**numeric_field_values)

    price_change_month_ago = models.DecimalField(**numeric_field_values)
    date_month_ago = models.DateField(null=True, blank="True")
    price_change_year_ago = models.DecimalField(**numeric_field_values)
    date_year_ago = models.DateField(null=True, blank="True")

    class Meta:
        abstract = True


class EntityLiveFuture(TradableEntity):
    expiry_date = models.DateField()

    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EntityLiveOpenInterest(BaseModel):
    lastest_open_interest = models.DecimalField(**numeric_field_values)
    previous_open_interest = models.DecimalField(**numeric_field_values)
    change_in_open_interest = models.DecimalField(**numeric_field_values)
    average_open_interest = models.DecimalField(**numeric_field_values)
    volume_open_interest = models.DecimalField(**numeric_field_values)
    future_value = models.DecimalField(**numeric_field_values)
    option_value = models.DecimalField(**numeric_field_values)
    total_value = models.DecimalField(**numeric_field_values)
    underlying_value = models.DecimalField(**numeric_field_values)

    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EntityLiveOptionChain(BaseModel):
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

    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
