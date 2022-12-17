from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
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
    StockScreener,
    StockScreenerSection,
    StockScreenerSectionItem,
    StockWatchlist,
    StockWatchlistItem,
    TodoFolder,
    TodoTask,
    TransactionType,
)
from ontrack.users.models.user import Setting, UserProfile
from ontrack.utils.base.enum import AccountType as at

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
admin.site.register(AccountInterestRate)
admin.site.register(AccountCheque)
admin.site.register(TodoFolder)
admin.site.register(TodoTask)


class StockScreenerSectionInline(admin.StackedInline):
    model = StockScreenerSection
    extra = 0


class StockScreenerSectionItemInline(admin.StackedInline):
    model = StockScreenerSectionItem
    extra = 0


class StockWatchlistItemInline(admin.StackedInline):
    model = StockWatchlistItem
    extra = 0
    raw_id_fields = [
        "equity",
        "index",
    ]


@admin.register(StockWatchlistItem)
class StockWatchlistItemAdmin(admin.ModelAdmin):
    raw_id_fields = [
        "equity",
        "index",
    ]


@admin.register(StockWatchlist)
class StockWatchlistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name__icontains",)

    inlines = [StockWatchlistItemInline]
    list_per_page = 100


@admin.register(StockScreener)
class StockScreenerAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name__icontains",)

    inlines = [StockScreenerSectionInline]
    list_per_page = 100


@admin.register(StockScreenerSection)
class StockScreenerSectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "link_to_screener",
        "operator",
        "weightage",
        "enabled",
    )
    list_filter = ("screener__name",)
    search_fields = (
        "name__icontains",
        "screener__name__icontains",
    )

    def link_to_screener(self, obj):
        link = reverse("admin:users_stockscreener_change", args=[obj.screener_id])
        return format_html('<a href="{}">{}</a>', link, obj.screener.name)

    link_to_screener.short_description = "Screener"

    inlines = [StockScreenerSectionItemInline]
    list_per_page = 100


@admin.register(StockScreenerSectionItem)
class StockScreenerSectionItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "link_to_screener",
        "link_to_section",
        "link_to_item",
        "item_category",
        "operator",
        "weightage",
        "level",
        "enabled",
    )
    list_filter = ("section__screener__name",)
    search_fields = (
        "name__icontains",
        "section__name__icontains",
        "section__screener__name__icontains",
    )

    def link_to_screener(self, obj):
        link = reverse(
            "admin:users_stockscreener_change", args=[obj.section.screener_id]
        )
        return format_html('<a href="{}">{}</a>', link, obj.screener_name)

    def link_to_section(self, obj):
        link = reverse("admin:users_stockscreenersection_change", args=[obj.section_id])
        return format_html('<a href="{}">{}</a>', link, obj.section_name)

    def link_to_item(self, obj):
        link = reverse("admin:market_marketscreener_change", args=[obj.item_id])
        return format_html('<a href="{}">{}</a>', link, obj.item.name)

    link_to_item.short_description = "Item"
    link_to_section.short_description = "Section"
    link_to_screener.short_description = "Screener"

    list_per_page = 100


@admin.action(description="Mark selected records as in active")
def make_inactive(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "account_type",
        "is_active",
    )
    list_filter = (
        "is_active",
        "account_type",
    )
    search_fields = (
        "name__icontains",
        "account_type",
    )
    list_per_page = 100
    actions = [make_inactive]


@admin.register(DematAccount)
class DematAccountAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "account":
            kwargs["queryset"] = Account.backend.filter(
                account_type_id=at.TRADING_ACCOUNT, is_active=True
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
