from django.contrib import admin

from .models import (
    MarketBroker,
    MarketDayType,
    MarketExchange,
    MarketSector,
    MarketTradingStrategy,
    MarketTradingStrategySymbol,
)

# Register your models here.


@admin.register(MarketExchange)
class MarketExchangeAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "data_refresh_time", "time_zone")
    list_filter = ("time_zone",)
    search_fields = ("name__icontains",)


@admin.register(MarketDayType)
class MarketDayTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "exchange")
    list_filter = ("exchange",)
    search_fields = ("name__icontains",)

    # def exchange_link(self, obj):
    #     result = MarketExchange.objects.filter(day_types=obj).first()
    #     url = (
    #         reverse("admin:admin_lookup_marketexchange_changelist")
    #         + "?"
    #         + urlencode({"marketexchange__id": f"{result.id}"})
    #     )
    #     return format_helpers(f'<a href="{url}">Exchange</a>')

    # exchange_link.short_description = "Exchange"

    # start_time_property.short_description = _("Start Time")


admin.site.register(MarketBroker)
admin.site.register(MarketSector)
admin.site.register(MarketTradingStrategy)
admin.site.register(MarketTradingStrategySymbol)
