from django.contrib import admin

from .models import (  # AccountType,; FieldDataType,; FieldType,; FieldTypeCategory,; InterestRate,; TransactionType,
    Currency,
    Setting,
)

# Register your models here.
admin.site.register(Currency)
# admin.site.register(FieldDataType)
# admin.site.register(FieldTypeCategory)
# admin.site.register(FieldType)
# admin.site.register(AccountType)
# admin.site.register(TransactionType)
# admin.site.register(InterestRate)
admin.site.register(Setting)
