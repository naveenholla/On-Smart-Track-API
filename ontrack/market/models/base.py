from django.db import models
from django.db.models import Avg
from rest_framework.reverse import reverse

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
    ticker_symbol = models.CharField(max_length=200, unique=True, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)
    lot_size = models.IntegerField(default=0, null=True, blank=True)
    strike_difference = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now=True)

    details_view_name = ""

    @property
    def get_absolute_url(self):
        return reverse(self.details_view_name, kwargs={"slug__iexact": self.slug})

    @property
    def average_delivery_quantity(self):
        if hasattr(self, "_average_delivery_quantity"):
            return self._average_delivery_quantity
        return self.eod_data.aggregate(Avg("delivery_quantity"))

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

    @property
    def top_central_pivot(self):
        if self.high_price and self.low_price:
            return (self.high_price + self.low_price) / 2
        return 0

    @property
    def pivot(self):
        if self.high_price and self.low_price and self.close_price:
            return (self.high_price + self.close_price + self.low_price) / 3
        return 0

    @property
    def bottom_central_pivot(self):
        return (self.pivot - self.top_central_pivot) + self.pivot

    @property
    def resistance_3(self):
        if self.high_price and self.low_price:
            return self.high_price + (2 * (self.pivot - self.low_price))
        return 0

    @property
    def resistance_2(self):
        if self.high_price and self.low_price:
            return self.pivot + (self.high_price - self.low_price)
        return 0

    @property
    def resistance_1(self):
        if self.low_price:
            return (2 * self.pivot) - self.low_price
        return 0

    @property
    def support_1(self):
        if self.high_price:
            return (2 * self.pivot) - self.high_price
        return 0

    @property
    def support_2(self):
        if self.high_price and self.low_price:
            return self.pivot - (self.high_price - self.low_price)
        return 0

    @property
    def support_3(self):
        if self.high_price and self.low_price:
            return self.low_price - (2 * (self.high_price - self.pivot))
        return 0

    @property
    def central_pivot_range(self):
        if self.high_price and self.low_price:
            return abs((((self.high_price + self.low_price) / 2) - self.pivot) * 2)
        return 0

    @property
    def open_high(self):
        if self.open_price and self.high_price:
            return self.open_price == self.high_price
        return False

    @property
    def open_low(self):
        if self.open_price and self.low_price:
            return self.open_price == self.low_price
        return False

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
    strike_price = models.DecimalField(**numeric_field_values)
    instrument = models.CharField(max_length=50, choices=InstrumentType.choices)
    option_type = models.CharField(
        max_length=50, choices=OptionType.choices, null=True, blank=True
    )
    expiry_date = models.DateField()
    open_interest = models.DecimalField(**numeric_field_values)
    change_in_open_interest = models.DecimalField(**numeric_field_values)
    percentage_change_in_oi = models.DecimalField(**numeric_field_values)
    total_traded_volume = models.DecimalField(**numeric_field_values)
    implied_volatility = models.DecimalField(**numeric_field_values)
    last_traded_price = models.DecimalField(**numeric_field_values)
    last_traded_quantity = models.DecimalField(**numeric_field_values)
    last_traded_time = models.DateTimeField(null=True, blank=True)
    change = models.DecimalField(**numeric_field_values)
    percentage_change = models.DecimalField(**numeric_field_values)
    total_buy_quantity = models.DecimalField(**numeric_field_values)
    total_sell_quantity = models.DecimalField(**numeric_field_values)
    bid_quantity = models.DecimalField(**numeric_field_values)
    bid_price = models.DecimalField(**numeric_field_values)
    ask_quantity = models.DecimalField(**numeric_field_values)
    ask_price = models.DecimalField(**numeric_field_values)
    underlying_value = models.DecimalField(**numeric_field_values)

    date = models.DateTimeField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EntityCalcutatedValues(BaseModel):
    pivot = models.DecimalField(**numeric_field_values)
    central_pivot_range = models.DecimalField(**numeric_field_values)
    average_central_pivot_range = models.DecimalField(**numeric_field_values)
    candle_type = models.CharField(max_length=100)
    relative_strength = models.DecimalField(**numeric_field_values)
    relative_strength_indicator = models.DecimalField(**numeric_field_values)

    sma_5 = models.DecimalField(**numeric_field_values)
    sma_20 = models.DecimalField(**numeric_field_values)
    sma_50 = models.DecimalField(**numeric_field_values)
    sma_100 = models.DecimalField(**numeric_field_values)
    sma_200 = models.DecimalField(**numeric_field_values)

    ema_5 = models.DecimalField(**numeric_field_values)
    ema_20 = models.DecimalField(**numeric_field_values)
    ema_50 = models.DecimalField(**numeric_field_values)
    ema_100 = models.DecimalField(**numeric_field_values)
    ema_200 = models.DecimalField(**numeric_field_values)

    standard_deviation = models.DecimalField(**numeric_field_values)

    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
