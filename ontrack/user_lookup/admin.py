from django.contrib import admin

from ontrack.user_lookup.models import (
    Account,
    AccountCheque,
    AccountInterestRate,
    AccountType,
    DematAccount,
    InterestRate,
    Person,
    TodoFolder,
    TodoTask,
    TransactionType,
)

# Register your models here.


admin.site.register(AccountType)
admin.site.register(TransactionType)
admin.site.register(InterestRate)
admin.site.register(Person)
admin.site.register(Account)
admin.site.register(DematAccount)
admin.site.register(AccountInterestRate)
admin.site.register(AccountCheque)
admin.site.register(TodoFolder)
admin.site.register(TodoTask)
