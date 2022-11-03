import csv

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
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


class FnoStockFilter(SimpleListFilter):
    title = "Is FNO Stock"
    parameter_name = "lot_size"

    def lookups(self, request, model_admin):
        return (("fno", "fno"), ("non_fno", "non-fno"))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        if self.value().lower() == "fno":
            return queryset.filter(lot_size__gt=0)
        elif self.value().lower() == "non_fno":
            return queryset.filter(lot_size=0)


class MarketDayCategoryInline(admin.StackedInline):
    model = MarketDayCategory
    extra = 0


@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "symbol",
        "start_time",
        "end_time",
        "data_refresh_time",
        "time_zone",
    )
    list_filter = ("time_zone",)
    search_fields = (
        "name__icontains",
        "symbol__icontains",
    )

    inlines = [MarketDayCategoryInline]
    list_per_page = 100


@admin.register(MarketDayType)
class MarketDayTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name__icontains",)


@admin.register(MarketDayCategory)
class MarketDayCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "exchange",
        "code",
        "display_name",
        "parent_name",
    )
    list_filter = (
        "exchange",
        "parent_name",
    )
    search_fields = (
        "exchange__name__icontains",
        "exchange__symbol__icontains",
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
    list_display = (
        "name",
        "symbol",
        "slug",
        "lot_size",
        "is_fno",
    )
    search_fields = (
        "name__icontains",
        "symbol__icontains",
    )
    list_filter = (FnoStockFilter,)
    actions = ["export_as_csv"]

    def is_fno(self, obj=None):
        if obj:
            return obj.lot_size > 0
        else:
            return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["slug"]  # read only while editing
        else:
            return []  # not read only by creation


@admin.register(Index)
class IndexAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        "name",
        "symbol",
        "slug",
        "lot_size",
        "is_fno",
    )
    search_fields = (
        "name__icontains",
        "symbol__icontains",
    )
    list_filter = (FnoStockFilter,)
    actions = ["export_as_csv"]

    def is_fno(self, obj=None):
        if obj:
            return obj.lot_size > 0
        else:
            return False

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
        "ordinal",
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
    actions = [
        "export_as_csv",
    ]

    ordering = [
        "index__ordinal",
        "-equity_weightage",
    ]

    def link_to_index(self, obj):
        link = reverse("admin:market_index_change", args=[obj.index_id])
        return format_html('<a href="{}">{}</a>', link, obj.index.name)

    link_to_index.short_description = "Index"

    def ordinal(self, obj):
        return obj.index.ordinal

    ordinal.admin_order_field = "index__ordinal"


admin.site.register(MarketBroker)
admin.site.register(MarketSector)
admin.site.register(MarketTradingStrategy)
admin.site.register(MarketTradingStrategySymbol)
