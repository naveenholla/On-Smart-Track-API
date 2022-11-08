from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from ontrack.users.forms import UserAdminChangeForm, UserAdminCreationForm
from ontrack.users.models.lookup import (
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
from ontrack.users.models.user import Setting, UserProfile

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


# class UserProfileInLine(admin.StackedInline):
#     model = UserProfile
#     can_delete = False

# class AccountsUserAdmin(AuthUserAdmin):
#     def add_view(self, *args, **kwargs):
#         self.inlines = []
#         return super(AccountsUserAdmin, self).add_view(*args, **kwargs)

#     def change_view(self, *args, **kwargs):
#         self.inlines = [UserProfileInLine]
#         return super(AccountsUserAdmin, self).change_view(*args, **kwargs)

# admin.site.unregister(User)
# admin.site.register(User, AccountsUserAdmin)

admin.site.register(UserProfile)
admin.site.register(Setting)

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
