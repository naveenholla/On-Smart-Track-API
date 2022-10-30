from django.contrib import admin

from .models import Currency, Setting

# Register your models here.
admin.site.register(Currency)


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = (
        "key",
        "value",
    )
    search_fields = (
        "key__icontains",
        "value__icontains",
    )
