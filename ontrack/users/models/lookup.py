from django.db import models
from django_cryptography.fields import encrypt

from ontrack.lookup.models import Currency
from ontrack.market.models.lookup import (
    Equity,
    Index,
    MarketBroker,
    MarketScreener,
    MarketScreenerCategory,
)
from ontrack.users.managers.manager import (
    StockScreenerManager,
    StockWatchlistManager,
    UserManager,
)
from ontrack.users.models.user import User
from ontrack.utils.base.enum import DematAccountAccessType, FrequencyType, OperatorType
from ontrack.utils.base.model import BaseModel


class AccountType(BaseModel):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self",
        related_name="parent_record",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_financial = models.BooleanField(default=False)
    icon = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    ordinal = models.IntegerField()

    class Meta(BaseModel.Meta):
        ordering = ["name"]

    def __str__(self):
        return self.name


class TransactionType(BaseModel):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        "self",
        related_name="parent_record",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    is_expenses = models.BooleanField(null=True)
    is_exclude_from_report = models.BooleanField(default=False)
    icon = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    ordinal = models.IntegerField()

    class Meta(BaseModel.Meta):
        ordering = ["name"]

    def __str__(self):
        return self.name


class InterestRate(BaseModel):
    account_type = models.ForeignKey(
        AccountType, related_name="interest_rates", on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    imterest_rate = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account_type


# Create your models here.
class Person(BaseModel):
    user = models.ForeignKey(User, related_name="persons", on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta(BaseModel.Meta):
        ordering = ["name"]

    def __str__(self):
        return self.name


class Account(BaseModel):
    user = models.ForeignKey(User, related_name="accounts", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    parent = models.ForeignKey(
        "self",
        related_name="parent_record",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    account_type = models.ForeignKey(
        AccountType, related_name="accounts", on_delete=models.CASCADE
    )
    person = models.ManyToManyField(Person, related_name="accounts")
    available_balance = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    ledger_balance = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    credit_limit = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    exclude_from_reports = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    currency = models.ForeignKey(
        Currency, related_name="accounts", on_delete=models.CASCADE
    )

    backend = UserManager()

    class Meta(BaseModel.Meta):
        ordering = ["name"]

    def __str__(self):
        return self.name


class DematAccount(BaseModel):
    account = models.OneToOneField(
        Account, related_name="demat_account", on_delete=models.CASCADE
    )
    institute = models.ForeignKey(
        MarketBroker, related_name="demat_account", on_delete=models.CASCADE
    )
    account_type = models.CharField(
        max_length=50,
        choices=DematAccountAccessType.choices,
        default=DematAccountAccessType.DEMAT,
    )
    client_id = models.CharField(max_length=50)
    app_key = encrypt(models.CharField(max_length=500, null=True, blank=True))
    app_secret = encrypt(models.CharField(max_length=500, null=True, blank=True))
    access_token = encrypt(models.CharField(max_length=500, null=True, blank=True))
    is_login_initated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    Funds = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    available_cash = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    margin = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)

    backend = UserManager()

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name


class AccountInterestRate(BaseModel):
    account = models.ForeignKey(
        Account, related_name="interest_rates", on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    imterest_rate = models.DecimalField(max_digits=18, decimal_places=4)
    emi_value = models.DecimalField(max_digits=18, decimal_places=4)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name


class StockScreener(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    enabled = models.BooleanField(default=True)

    backend = StockScreenerManager()

    def __str__(self):
        return self.name


class StockScreenerSection(BaseModel):
    screener = models.ForeignKey(
        StockScreener, on_delete=models.CASCADE, related_name="sections"
    )
    name = models.CharField(max_length=100, unique=True)
    operator = models.CharField(
        max_length=50, choices=OperatorType.choices, default=OperatorType.AND
    )
    weightage = models.IntegerField(default=3)
    enabled = models.BooleanField(default=True)

    backend = StockScreenerManager()

    def __str__(self):
        return f"{self.screener.name} - {self.name}"


class StockScreenerSectionItem(BaseModel):
    section = models.ForeignKey(
        StockScreenerSection, on_delete=models.CASCADE, related_name="items"
    )
    item = models.ForeignKey(
        MarketScreener, on_delete=models.CASCADE, blank=True, null=True
    )
    item_category = models.ForeignKey(
        MarketScreenerCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    operator = models.CharField(
        max_length=50, choices=OperatorType.choices, default=OperatorType.AND
    )
    level = models.IntegerField(default=3)
    weightage = models.IntegerField(default=3)
    enabled = models.BooleanField(default=True)

    backend = StockScreenerManager()

    @property
    def section_name(self):
        return f"{self.section.name}"

    @property
    def screener_name(self):
        return f"{self.section.screener.name}"

    @property
    def display_name(self):
        if self.item:
            return f"{self.section} - {self.item}"

        if self.item_category:
            return f"{self.section} - {self.item_category}"

    def __str__(self):
        return self.display_name


class StockWatchlist(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    date = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    backend = StockWatchlistManager()

    def __str__(self):
        return self.name


class StockWatchlistItem(BaseModel):
    watchlist = models.ForeignKey(
        StockWatchlist, on_delete=models.CASCADE, related_name="items"
    )
    equity = models.ForeignKey(Equity, on_delete=models.CASCADE, blank=True, null=True)
    index = models.ForeignKey(Index, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=True)

    backend = StockWatchlistManager()

    def __str__(self):
        if self.equity:
            return f"{self.watchlist} - {self.equity.symbol.upper()}"
        elif self.index:
            return f"{self.watchlist} - {self.index.symbol.upper()}"

        return self.watchlist


# class AccountField(BaseModel):
#     account = models.ForeignKey(
#         Account, related_name="account_fields", on_delete=models.CASCADE
#     )
#     field_type = models.ForeignKey(
#         FieldType, related_name="account_fields", on_delete=models.CASCADE
#     )
#     field_value = models.TextField(null=True, blank=True)

#     class Meta(BaseModel.Meta):
#         ordering = ["-created_at"]

#     def __str__(self):
#         return self.symbol


class AccountCheque(BaseModel):
    account = models.ForeignKey(
        Account, related_name="account_cheques", on_delete=models.CASCADE
    )
    cheque_number = models.CharField(max_length=50)
    description = models.CharField(max_length=50)
    Date = models.DateTimeField(null=True, blank=True)
    Amount = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    IsBudget = models.TextField(null=False)
    is_cancelled = models.TextField(null=False)
    is_used = models.TextField(null=False)
    is_valid = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.symbol


class TodoFolder(BaseModel):
    user = models.ForeignKey(
        User, related_name="todo_folders", on_delete=models.CASCADE
    )
    folder_name = models.CharField(max_length=50)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class TodoTask(BaseModel):
    user = models.ForeignKey(User, related_name="todo_tasks", on_delete=models.CASCADE)
    folder = models.ForeignKey(
        TodoFolder, related_name="todo_tasks", on_delete=models.CASCADE
    )
    subject = models.CharField(max_length=50)
    details = models.TextField(null=True, blank=True)
    default_amount = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    priority = models.IntegerField(null=True, blank=True)
    reminder = models.BooleanField(default=False)
    next_due_date = models.DateTimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class TodoTaskFrequency(BaseModel):
    task = models.OneToOneField(
        TodoTask, related_name="todo_task_frequency", on_delete=models.CASCADE
    )
    frequency = models.CharField(
        max_length=50, choices=FrequencyType.choices, default=FrequencyType.MONTHLY
    )
    frequency_count = models.IntegerField()
    frequency_start_date = models.DateTimeField()
    frequency_end_date = models.DateTimeField(null=True, blank=True)
    timezone = models.CharField(max_length=100)
    day_of_week = models.CharField(max_length=100)
    day_of_month = models.CharField(max_length=100)
    week_of_month = models.CharField(max_length=100)
    month_of_year = models.CharField(max_length=100)
    occurence_count = models.IntegerField()
    remainder_time = models.TimeField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
