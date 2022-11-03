from django.contrib import admin

from .models import Currency, Setting

# Register your models here.
admin.site.register(Currency)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "value",
        "key_type",
    )
    search_fields = (
        "key__icontains",
        "value__icontains",
    )
    list_filter = ("key_type",)
