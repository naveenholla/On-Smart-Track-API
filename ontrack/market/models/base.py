from django.db import models

from ontrack.utils.base.enum import InstrumentType, OptionType

numeric_field_values = {
    "max_digits": 18,
    "decimal_places": 4,
    "null": True,
    "blank": True,
}


class MarketEntity(models.Model):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200, unique=True)
    chart_symbol = models.CharField(max_length=200, unique=True, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)
    lot_size = models.IntegerField(default=0, null=True, blank=True)
    strike_difference = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class TradableEntity(models.Model):
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


class EndOfDayData(models.Model):
    traded_quantity = models.DecimalField(**numeric_field_values)
    traded_value = models.DecimalField(**numeric_field_values)
    number_of_trades = models.DecimalField(**numeric_field_values)
    quantity_per_trade = models.DecimalField(**numeric_field_values)
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DerivativeEndOfDay(models.Model):
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
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
