from django.contrib import admin

from ontrack.market.models.lookup import (
    Equity,
    EquityIndex,
    Exchange,
    Index,
    MarketBroker,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
    MarketSector,
    MarketTradingStrategy,
    MarketTradingStrategySymbol,
)

# Register your models here.


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "data_refresh_time", "time_zone")
    list_filter = ("time_zone",)
    search_fields = ("name__icontains",)


@admin.register(MarketDayType)
class MarketDayTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "exchange")
    list_filter = ("exchange",)
    search_fields = ("name__icontains",)


@admin.register(MarketDay)
class MarketDayAdmin(admin.ModelAdmin):
    list_display = ("daytype", "category", "date", "day")
    list_filter = (
        "daytype",
        "category",
    )
    search_fields = ("date",)


admin.site.register(Equity)
admin.site.register(Index)
admin.site.register(EquityIndex)
admin.site.register(MarketDayCategory)
admin.site.register(MarketBroker)
admin.site.register(MarketSector)
admin.site.register(MarketTradingStrategy)
admin.site.register(MarketTradingStrategySymbol)
