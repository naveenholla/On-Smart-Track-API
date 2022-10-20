from django.db import models

from ontrack.market.managers.equity import EquityEndOfDayPullManager
from ontrack.market.models.lookup import Equity
from ontrack.utils.base.enum import InstrumentType, OptionType
from ontrack.utils.base.model import BaseModel


class EquityInsiderTrade(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="insider_trades", on_delete=models.CASCADE
    )
    category_of_person = models.CharField(max_length=100)
    no_of_shares = models.IntegerField()
    value_of_shares = models.DecimalField(max_digits=18, decimal_places=4)
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


class EquityEndOfDay(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="equity_eod_datas", on_delete=models.CASCADE
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
    last_price = models.DecimalField(
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
    avg_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    traded_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    turn_overs_in_lacs = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    number_of_trades = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    delivery_quantity = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    delivery_percentage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    quantity_per_trade = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    promotor_holding_percentage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    average_quantity_per_trade = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    average_volumn = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    average_delivery_percentage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    average_open_interest = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    date = models.DateField()
    pull_date = models.DateTimeField(auto_now=True)

    datapull_manager = EquityEndOfDayPullManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.equity.name


class EquityDerivativeEndOfDay(BaseModel):
    equity = models.ForeignKey(
        Equity, related_name="equity_derivative_eod_datas", on_delete=models.CASCADE
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


class LiveEquityData(BaseModel):
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


class LiveEquityOptionChain(BaseModel):
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


class LiveEquityDerivative(BaseModel):
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
