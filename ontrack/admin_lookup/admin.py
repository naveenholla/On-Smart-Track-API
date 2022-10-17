from django.contrib import admin

from .models import Currency, Setting

# Register your models here.
admin.site.register(Currency)
admin.site.register(Setting)
