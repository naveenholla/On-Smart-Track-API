from django.db import models
from django_cryptography.fields import encrypt

from ontrack.market_lookup.models.lookup import Exchange, MarketTradingStrategy
from ontrack.user_lookup.models import Account, AccountCheque, TodoTask, TransactionType
from ontrack.utils.base.enum import (
    DirectionType,
    OptionType,
    OrderExitReasonType,
    OrderStatusType,
    OrderType,
    OrderValidityType,
    SegmentType,
)
from ontrack.utils.base.model import BaseModel


# Create your models here.
class AccountSession(BaseModel):
    account = models.ForeignKey(
        Account, related_name="sessions", on_delete=models.CASCADE
    )
    access_token = encrypt(models.CharField(max_length=500))
    is_login_initated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name


class AccountTransaction(BaseModel):
    account = models.ForeignKey(
        Account, related_name="transactions", on_delete=models.CASCADE
    )
    account_cheque = models.OneToOneField(
        AccountCheque,
        related_name="transactions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    todo_task = models.OneToOneField(TodoTask, on_delete=models.CASCADE)
    transaction_type = models.ForeignKey(
        TransactionType, related_name="transactions", on_delete=models.CASCADE
    )
    decription = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    account_opening_balance = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    account_close_balance = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    principal_amount = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    interest_amount = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    occurance_date = models.DateTimeField()
    is_budget = models.BooleanField(default=False)
    is_pursed = models.BooleanField(default=False)
    sequence_number = models.IntegerField(null=True, blank=True)
    previous_transaction_id = models.IntegerField(null=True, blank=True)
    linked_transaction_id = models.IntegerField(null=True, blank=True)
    notes = models.CharField(max_length=100)
    bill_path = models.CharField(max_length=100)
    exclude_from_reports = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name


class AccountStrategies(BaseModel):
    account = models.ForeignKey(
        Account, related_name="strategies", on_delete=models.CASCADE
    )
    strategy = models.ForeignKey(
        MarketTradingStrategy,
        related_name="account_strategies",
        on_delete=models.CASCADE,
    )
    capital = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )  # Capital to trade (This is the margin you allocate from your broker account for this strategy)
    leverage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )  # 1x, 2x, 3x Etc
    capital_per_set = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )  # Applicable if isFnO is True (Set means 1CE/1PE or 2CE/2PE etc based on your strategy logic)
    is_active = models.BooleanField(default=True)
    is_hedged = models.BooleanField(default=False)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name


class StrategyTrade(BaseModel):
    account_strategy = models.ForeignKey(
        AccountStrategies, related_name="trades", on_delete=models.CASCADE
    )
    session = encrypt(models.CharField(max_length=500))
    initiated_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=50, choices=OrderStatusType.choices, null=True, blank=True
    )
    exchange = models.ForeignKey(
        Exchange, related_name="trades", on_delete=models.CASCADE
    )
    symbol = models.CharField(max_length=100)
    symbol_current_market_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    exited_time = models.DateTimeField(null=True, blank=True)
    pnl = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    capital = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name


class StrategyTradeOrder(BaseModel):
    strategy = models.ForeignKey(
        StrategyTrade, related_name="orders", on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        "self",
        related_name="parent_record",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    order_type = models.CharField(
        max_length=50, choices=OrderType.choices, null=True, blank=True
    )
    option_type = models.CharField(
        max_length=50, choices=OptionType.choices, null=True, blank=True
    )
    quantity = models.IntegerField()
    filled_quantity = models.IntegerField()
    pending_quantity = models.IntegerField()
    status = models.CharField(
        max_length=50, choices=OrderStatusType.choices, null=True, blank=True
    )
    institute_order_Id = models.CharField(max_length=50)
    segment = models.CharField(
        max_length=50, choices=SegmentType.choices, null=True, blank=True
    )  # equity | future | option
    entry_price = models.DecimalField(max_digits=18, decimal_places=4)
    exit_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    initial_stoploss_price = models.DecimalField(max_digits=18, decimal_places=4)
    trigger_Price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    average_Price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    current_market_price = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    direction = models.CharField(
        max_length=50, choices=DirectionType.choices, null=True, blank=True
    )
    order_validate_type = models.CharField(
        max_length=50, choices=OrderValidityType.choices, null=True, blank=True
    )
    order_execute_time = models.DateTimeField()
    order_exit_time = models.DateTimeField(null=True, blank=True)
    last_order_check_time = models.DateTimeField(null=True, blank=True)
    exit_Reason = models.CharField(
        max_length=50, choices=OrderExitReasonType.choices, null=True, blank=True
    )
    message_from_instititue = models.CharField(max_length=200)
    brokerage = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    stt = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    transaction_charges = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    gst = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    sebi = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    clearing_charges = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    stamp_duty = models.DecimalField(
        max_digits=18, decimal_places=4, null=True, blank=True
    )
    expiry_date = models.DateTimeField(null=True, blank=True)
    is_weekly_expiry = models.BooleanField(null=True, blank=True)
    option_price = models.IntegerField(null=True, blank=True)
    lot_size = models.IntegerField(null=True, blank=True)
    learning_notes = models.CharField(max_length=200)

    class Meta(BaseModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return self.account.name
