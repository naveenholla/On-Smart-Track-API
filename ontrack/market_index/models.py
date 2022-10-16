from django.db import models

from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel

from ..market_equity.models import Equity
from ..market_lookup.models import MarketExchange
from .manager import EquityIndexPullManager, IndexEndOfDayPullManager, IndexPullManager


# Create your models here.
class Index(BaseModel):
    exchange = models.ForeignKey(
        MarketExchange, related_name="indices", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200, unique=True)
    chart_symbol = models.CharField(max_length=200, unique=True, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)
    lot_size = models.IntegerField(default=0, null=True, blank=True)
    strike_difference = models.IntegerField(null=True, blank=True)
    ordinal = models.IntegerField()
    is_sectoral = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    datapull_manager = IndexPullManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class EquityIndex(BaseModel):
    indice = models.ForeignKey(
        Index,
        related_name="indices",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    equity = models.ForeignKey(
        Equity, related_name="equity_indices", on_delete=models.CASCADE
    )
    equity_weightage = models.DecimalField(max_digits=18, decimal_places=4)
    sector = models.CharField(max_length=100, null=True, blank=True)
    sector_weightage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    last_update_date = models.DateField(null=True, blank=True, auto_now=True)

    datapull_manager = EquityIndexPullManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class DerivativeEndOfDay(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="derivative_eod_datas", on_delete=models.CASCADE
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


class IndiceEndOfDay(BaseModel):
    indice = models.ForeignKey(
        Index, related_name="indice_eod_datas", on_delete=models.CASCADE
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
