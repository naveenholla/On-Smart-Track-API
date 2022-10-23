from django.db import models

from ontrack.utils.base.model import BaseModel

numeric_field_values = {
    "max_digits": 18,
    "decimal_places": 4,
    "null": True,
    "blank": True,
}


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

    class Meta(BaseModel.Meta):
        abstract = True


class TradableEntityEndOfDayData(TradableEntity):
    traded_quantity = models.DecimalField(**numeric_field_values)
    traded_value = models.DecimalField(**numeric_field_values)
    number_of_trades = models.DecimalField(**numeric_field_values)
    quantity_per_trade = models.DecimalField(**numeric_field_values)
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    class Meta(BaseModel.Meta):
        abstract = True
