from django.db import models
from timezone_field import TimeZoneField

from ontrack.utils.base.enum import (
    HolidayCategoryType,
    HolidayParentCategoryType,
    MarketDayTypeEnum,
    OrderValidityType,
    SegmentType,
    WeekDayType,
)
from ontrack.utils.base.model import BaseModel

from ..manager import (
    EquityIndexPullManager,
    EquityPullManager,
    ExchangePullManager,
    IndexPullManager,
)


class Exchange(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    data_refresh_time = models.TimeField(null=True, blank=True)
    time_zone = TimeZoneField(default="Asia/Kolkata", choices_display="WITH_GMT_OFFSET")

    datapull_manager = ExchangePullManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class MarketDayType(BaseModel):
    name = models.CharField(max_length=50, choices=MarketDayTypeEnum.choices)
    exchange = models.ForeignKey(
        Exchange, related_name="day_types", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("exchange", "name")

    def __str__(self):
        return f"{self.exchange} - {self.name}"


class MarketDayCategory(BaseModel):
    day_type = models.ForeignKey(
        MarketDayType, related_name="categories", on_delete=models.CASCADE
    )
    parent_name = models.CharField(
        max_length=50, choices=HolidayParentCategoryType.choices
    )
    display_name = models.CharField(max_length=50, choices=HolidayCategoryType.choices)
    code = models.CharField(max_length=50)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("day_type", "code")

    def __str__(self):
        return f"{self.day_type} - {self.display_name}"


class MarketDay(BaseModel):
    category = models.ForeignKey(
        MarketDayCategory, related_name="days", on_delete=models.CASCADE
    )
    date = models.DateField(null=True, blank=True)
    day = models.CharField(
        max_length=50, choices=WeekDayType.choices, null=True, blank=True
    )
    is_working_day = models.BooleanField(default=False)
    description = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("category", "date", "day")

    def __str__(self):
        return f"{self.category} - {self.date.strftime('%d/%m/%Y %H:%M:%S')}"


class MarketBroker(BaseModel):
    name = models.CharField(max_length=50)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class MarketSector(BaseModel):
    date = models.DateField()
    macro_economic_sector_code = models.CharField(max_length=100)
    macro_economic_sector_name = models.CharField(max_length=100)
    sector_code = models.CharField(max_length=100)
    sector_name = models.CharField(max_length=100)
    industry_code = models.CharField(max_length=100)
    industry_name = models.CharField(max_length=100)
    basic_industry_code = models.CharField(max_length=100)
    basic_ndustry_name = models.CharField(max_length=100)
    defination = models.TextField()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.sector_name[0:50]


class MarketTradingStrategy(BaseModel):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    start_time = models.TimeField()
    max_entry_time = models.TimeField()
    square_off_time = models.TimeField()
    product_type = models.CharField(
        max_length=50, choices=OrderValidityType.choices, default=OrderValidityType.NRML
    )
    stop_loss_points = models.IntegerField()
    target_points = models.IntegerField()
    max_trades_per_day = models.IntegerField()
    is_fno = models.BooleanField(default=True)
    days_to_trade = models.CharField(max_length=200)
    is_expiry_day_trade = models.BooleanField(default=True)
    is_directional = models.BooleanField(default=True)
    is_intraday = models.BooleanField(default=True)
    can_run_parellel = models.BooleanField(default=True)
    placeMarketOrder = models.BooleanField(default=True)
    segment = models.CharField(
        max_length=50, choices=SegmentType.choices, default=SegmentType.Equity_Options
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class MarketTradingStrategySymbol(BaseModel):
    # List of stocks to be traded under this strategy
    symbol = models.CharField(max_length=100)
    strategy = models.ForeignKey(
        MarketTradingStrategy, related_name="strategy_symbols", on_delete=models.CASCADE
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class MarketEntity(BaseModel):
    name = models.CharField(max_length=200)
    symbol = models.CharField(max_length=200, unique=True)
    chart_symbol = models.CharField(max_length=200, unique=True, null=True, blank=True)
    slug = models.SlugField(blank=True, null=True)
    lot_size = models.IntegerField(default=0, null=True, blank=True)
    strike_difference = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        abstract = True

    def __str__(self):
        return self.symbol


class Equity(MarketEntity):
    exchange = models.ForeignKey(
        Exchange, related_name="equities", on_delete=models.CASCADE
    )

    datapull_manager = EquityPullManager()


# Create your models here.
class Index(MarketEntity):
    exchange = models.ForeignKey(
        Exchange, related_name="indices", on_delete=models.CASCADE
    )

    ordinal = models.IntegerField()
    is_sectoral = models.BooleanField(default=False)

    datapull_manager = IndexPullManager()


class EquityIndex(BaseModel):
    index = models.ForeignKey(
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
