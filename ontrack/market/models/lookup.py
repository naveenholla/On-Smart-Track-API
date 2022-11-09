from django.db import models
from timezone_field import TimeZoneField

from ontrack.market.managers.lookup import (
    EquityBackendManager,
    EquityIndexBackendManager,
    ExchangeBackendManager,
    IndexBackendManager,
    MarketDayBackendManager,
    MarketDayCategoryBackendManager,
    MarketDayTypeBackendManager,
)
from ontrack.market.models.base import MarketEntity
from ontrack.utils.base.enum import (
    HolidayCategoryType,
    HolidayParentCategoryType,
    MarketDayTypeEnum,
    OrderValidityType,
    SegmentType,
    WeekDayType,
)
from ontrack.utils.base.model import BaseModel


class Exchange(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    symbol = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    data_refresh_time = models.TimeField(null=True, blank=True)
    time_zone = TimeZoneField(default="Asia/Kolkata", choices_display="WITH_GMT_OFFSET")

    backend = ExchangeBackendManager()

    def get_days_by_category(
        self, day_type_name: MarketDayTypeEnum, category_name: HolidayCategoryType
    ):
        if not self.holiday_categories:
            return None

        category = self.holiday_categories.filter(
            display_name__iexact=category_name
        ).first()

        if not category or not category.days:
            return None

        days = category.days.filter(daytype__name__iexact=day_type_name)

        return list(days.all())

    @property
    def timezone_name(self):
        if hasattr(self.time_zone, "zone"):
            return self.time_zone.zone

        if hasattr(self.time_zone, "key"):
            return self.time_zone.key

        return None

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Exchange"
        verbose_name_plural = "Exchanges"

    def __str__(self):
        return self.symbol.upper()


class MarketDayType(BaseModel):
    name = models.CharField(
        max_length=50, choices=MarketDayTypeEnum.choices, unique=True
    )
    backend = MarketDayTypeBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Market Day Type"
        verbose_name_plural = "Market Day Types"

    def __str__(self):
        return f"{self.name}"


class MarketDayCategory(BaseModel):
    exchange = models.ForeignKey(
        Exchange, related_name="holiday_categories", on_delete=models.CASCADE
    )

    parent_name = models.CharField(
        max_length=50, choices=HolidayParentCategoryType.choices
    )
    display_name = models.CharField(max_length=50, choices=HolidayCategoryType.choices)
    code = models.CharField(max_length=50, unique=True)

    backend = MarketDayCategoryBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        unique_together = ("exchange", "code")
        verbose_name = "Market Day Category"
        verbose_name_plural = "Market Day Categories"

    def __str__(self):
        return f"{self.exchange} - {self.display_name} ({self.code})"


class MarketDay(BaseModel):
    category = models.ForeignKey(
        MarketDayCategory, related_name="days", on_delete=models.CASCADE
    )
    daytype = models.ForeignKey(
        MarketDayType, related_name="days", on_delete=models.CASCADE
    )
    date = models.DateField(null=True, blank=True)
    day = models.CharField(
        max_length=50, choices=WeekDayType.choices, null=True, blank=True
    )
    is_working_day = models.BooleanField(default=False)
    description = models.CharField(max_length=100, null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    backend = MarketDayBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["date"]
        unique_together = ("category", "date", "day")
        verbose_name = "Market Day"
        verbose_name_plural = "Market Days"

    def __str__(self):
        name = f"{self.category} - {self.daytype} - "
        if self.date is not None:
            name += f"{name}{self.date.strftime('%d/%m/%Y %H:%M:%S')}"
        else:
            name += f"{name}{self.day}"
        return name


class MarketBroker(BaseModel):
    name = models.CharField(max_length=50)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Market Broker"
        verbose_name_plural = "Market Brokers"

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
        verbose_name = "Market Sector"
        verbose_name_plural = "Market Sectors"

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
        verbose_name = "Trading Strategy"
        verbose_name_plural = "Trading Startegies"

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
        verbose_name = "Trading Startegy Symbol"
        verbose_name_plural = "Trading Strategy Symbols"

    def __str__(self):
        return self.symbol


class Equity(MarketEntity):
    exchange = models.ForeignKey(
        Exchange, related_name="equities", on_delete=models.CASCADE
    )

    isin_number = models.CharField(max_length=100, null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)

    details_view_name = "api_market:equity-detail"
    backend = EquityBackendManager()

    class Meta(BaseModel.Meta):
        verbose_name = "Equity"
        verbose_name_plural = "Equities"

    def __str__(self):
        return self.symbol.upper()


class Index(MarketEntity):
    exchange = models.ForeignKey(
        Exchange, related_name="indices", on_delete=models.CASCADE
    )

    ordinal = models.IntegerField()
    is_sectoral = models.BooleanField(default=False)

    backend = IndexBackendManager()

    class Meta(BaseModel.Meta):
        verbose_name = "Index"
        verbose_name_plural = "Indices"

    def __str__(self):
        return self.symbol.upper()


class EquityIndex(BaseModel):
    index = models.ForeignKey(
        Index,
        related_name="equity_indices",
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
    date = models.DateTimeField(auto_now=True)

    backend = EquityIndexBackendManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]
        verbose_name = "Equity Index Weightage"
        verbose_name_plural = "Equity Index Weightages"

    def __str__(self):
        return f"{self.index}:{self.equity} ({self.equity_weightage})"
