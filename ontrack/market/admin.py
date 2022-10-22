import csv

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html

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


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class MarketDayTypeInline(admin.StackedInline):
    model = MarketDayType
    extra = 0


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "data_refresh_time", "time_zone")
    list_filter = ("time_zone",)
    search_fields = ("name__icontains",)

    inlines = [MarketDayTypeInline]
    list_per_page = 100


@admin.register(MarketDayType)
class MarketDayTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "exchange")
    list_filter = ("exchange",)
    search_fields = ("name__icontains",)


@admin.register(MarketDayCategory)
class MarketDayCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "display_name",
        "parent_name",
    )
    list_filter = ("parent_name",)
    search_fields = (
        "display_name__icontains",
        "parent_name__icontains",
        "code__icontains",
    )


@admin.register(MarketDay)
class MarketDayAdmin(admin.ModelAdmin):
    list_display = ("daytype", "category", "date", "day")
    list_filter = (
        "daytype",
        "category",
    )
    search_fields = ("date",)


@admin.register(Equity)
class EquityAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("name", "symbol", "slug", "lot_size")
    search_fields = (
        "name__icontains",
        "symbol__icontains",
    )
    actions = ["export_as_csv"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["slug"]  # read only while editing
        else:
            return []  # not read only by creation


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ("name", "symbol", "slug", "lot_size")
    search_fields = (
        "name__icontains",
        "symbol__icontains",
    )
    actions = ["export_as_csv"]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["slug"]  # read only while editing
        else:
            return []  # not read only by creation


@admin.register(EquityIndex)
class EquityIndexAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        "id",
        "link_to_index",
        "equity",
        "equity_weightage",
        "sector",
        "sector_weightage",
    )
    search_fields = (
        "index__name__icontains",
        "equity__name__icontains",
        "index__symbol__icontains",
        "equity__symbol__icontains",
        "sector__icontains",
    )
    list_filter = (
        "index",
        "sector",
    )
    actions = ["export_as_csv"]

    def link_to_index(self, obj):
        link = reverse("admin:market_index_change", args=[obj.index_id])
        return format_html('<a href="{}">{}</a>', link, obj.index.name)

    link_to_index.short_description = "Index"


admin.site.register(MarketBroker)
admin.site.register(MarketSector)
admin.site.register(MarketTradingStrategy)
admin.site.register(MarketTradingStrategySymbol)
