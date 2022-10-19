from django.contrib import admin

from .models import (
    Exchange,
    MarketBroker,
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


admin.site.register(MarketBroker)
admin.site.register(MarketSector)
admin.site.register(MarketTradingStrategy)
admin.site.register(MarketTradingStrategySymbol)
