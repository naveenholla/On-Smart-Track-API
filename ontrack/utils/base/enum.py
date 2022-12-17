from django.db import models
from django.utils.translation import gettext_lazy as _


class SettingKeyType(models.TextChoices):
    CONFIGURATION = _("CONFIGURATION")
    EXECUTION_TIME = _("EXECUTION_TIME")


class AdminSettingKey(models.TextChoices):
    NO_OF_DAYS_AVG = _("NO_OF_DAYS_AVG")
    DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS = _("DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS")
    DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS = _("DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS")
    DATAPULL_EOD_DATA_PAUSE_HOURS = _("DATAPULL_EOD_DATA_PAUSE_HOURS")
    LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED = _(
        "LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED"
    )
    LIVE_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED = _(
        "LIVE_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED"
    )
    DEFAULT_START_DATE_EQUITY_DATA_PULL = _("DEFAULT_START_DATE_EQUITY_DATA_PULL")
    DEFAULT_START_DATE_INDEX_DATA_PULL = _("DEFAULT_START_DATE_INDEX_DATA_PULL")
    DEFAULT_START_DATE_PARTICIPANT_DATA_PULL = _(
        "DEFAULT_START_DATE_PARTICIPANT_DATA_PULL"
    )

    DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE = _("DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE")
    DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE = _(
        "DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE"
    )
    DATAPULL_EQUITY_EOD_LAST_PULL_DATE = _("DATAPULL_EQUITY_EOD_LAST_PULL_DATE")
    DATAPULL_INDICES_EOD_LAST_PULL_DATE = _("DATAPULL_INDICES_EOD_LAST_PULL_DATE")
    DATAPULL_PARTICIPANT_EOD_LAST_PULL_DATE = _(
        "DATAPULL_PARTICIPANT_EOD_LAST_PULL_DATE"
    )


class UserSettingKey(models.TextChoices):
    DEFAULT_THEME = "DEFAULT_THEME"
    DEFAULT_LANGUAGE = "DEFAULT_LANGUAGE"
    DEFAULT_CURRENCY = "DEFAULT_CURRENCY"
    DEFAULT_DATE_FORMAT = "DEFAULT_DATE_FORMAT"
    NOTIFICATION_ENABLED = "NOTIFICATION_ENABLED"


class ExpiryType(models.TextChoices):
    WEEKLY = _("WEEKLY")
    MONTHLY = _("MONTHLY")


class OrderValidityType(models.TextChoices):
    MIS = "MIS"
    NRML = "NRML"
    CNC = "CNC"


class MarketDayTypeEnum(models.TextChoices):
    TRADING_HOLIDAYS = "Trading Holidays"
    CLEARING_HOLIDAYS = "Clearing Holidays"
    WEEKLY_OFF_DAYS = "Weekly Off Days"
    SPECIAL_TRADING_DAYS = "Special Trading Days"


class HolidayParentCategoryType(models.TextChoices):
    CAPITAL_MARKET = "Capital Market"
    DEBT_MARKET = "Debt Market"
    DERIVATIVES_MARKET = "Derivatives Market"
    WEEKEND = "Weekend"
    SPECIAL_TRADING = "Special Trading"


class HolidayCategoryType(models.TextChoices):
    WEEKEND = "Weekend"
    SPECIAL_TRADING_HOURS = "Special Trading Hours"
    CORPORATE_BONDS = "Corporate Bonds"
    CURRENCY_DERIVATIVES = "Currency Derivatives"
    EQUITIES = "Equities"
    COMMODITY_DERIVATIVES = "Commodity Derivatives"
    EQUITY_DERIVATIVES = "Equity Derivatives"
    INTEREST_RATE_DERIVATIVES = "Interest Rate Derivatives"
    MUTUAL_FUNDS = "Mutual Funds"
    NEW_DEBT_SEGMENT = "New Debt Segment"
    NEGOTIATED_TRADE_REPORTING_PLATFORM = "Negotiated Trade Reporting Platform"
    SECURITIES_LENDING_BORROWING_SCHEMES = "Securities Lending & Borrowing Schemes"


class SegmentType(models.TextChoices):
    Equity_Delivery = "Equity_Delivery"
    Equity_Intraday = "Equity_Intraday"
    Equity_Futures = "Equity_Futures"
    Equity_Options = "Equity_Options"
    CURRENCY = "CURRENCY"
    COMMADITY = "COMMADITY"


class BrokerSegmentType(models.TextChoices):
    EQUITY = "EQUITY"
    FNO = "FNO"
    CURRENCY = "CURRENCY"
    COMMADITY = "COMMADITY"


class InstrumentType(models.TextChoices):
    FUTSTK = "FUTSTK"
    FUTIDX = "FUTIDX"
    OPTSTK = "OPTSTK"
    OPTIDX = "OPTIDX"
    CASH = "CASH"


class OptionType(models.TextChoices):
    CE = "CE"
    PE = "PE"


class ClientType(models.TextChoices):
    FII = "FII"
    DII = "DII"
    PRO = "PRO"
    CLIENT = "CLIENT"


class EntityType(models.TextChoices):
    STOCK = "STOCK"
    INDICES = "INDICES"


class OrderStatusType(models.TextChoices):
    CREATED = "CREATED"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    ACTIVE = "ACTIVE"
    OPEN_PENDING = "OPEN PENDING"
    VALIDATION_PENDING = "VALIDATION PENDING"
    PUT_ORDER_REQ_RECEIVED = "PUT ORDER REQ RECEIVED"
    TRIGGER_PENDING = "TRIGGER PENDING"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class OrderType(models.TextChoices):
    PRIMARY = "PRIMARY"
    STOP_LOSS = "STOP_LOSS"
    TARGET = "TARGET"


class DirectionType(models.TextChoices):
    NEUTRAL = "NEUTRAL"
    LONG = "LONG"
    SHORT = "SHORT"


class OperatorType(models.TextChoices):
    AND = "AND"
    OR = "OR"


class DematAccountAccessType(models.TextChoices):
    API = "API"
    DEMAT = "DEMAT"
    PUBLISHER = "PUBLISHER"
    INFOMATIONAL = "INFOMATIONAL"
    VIRTUAL = "VIRTUAL"


class OrderTriggerType(models.TextChoices):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    SL_MARKET = "SL_MARKET"
    SL_LIMIT = "SL_LIMIT"


class OrderExitReasonType(models.TextChoices):
    SL_HIT = "SL_HIT"
    TRAIL_SL_HIT = "TRAIL_SL_HIT"
    TARGET_HIT = "TARGET_HIT"
    SQUARE_OFF = "SQUARE_OFF"
    SL_CANCELLED = "SL_CANCELLED"
    TARGET_CANCELLED = "TARGET_CANCELLED"


class FrequencyType(models.TextChoices):
    DEFAULT = "DEFAULT"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    QUATERLY = "QUATERLY"
    HALFYEARLY = "HALFYEARLY"
    YEARLY = "YEARLY"


class ExchangeType(models.TextChoices):
    NSE = "NSE"


class WeekDayType(models.TextChoices):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class AccountType(models.IntegerChoices):
    CASH_IN_HAND = 1, _("Cash In Hand")
    LOANS = 2, _("Loans")
    LOYALTY_POINTS = 3, _("Loyalty Points")
    INVESTMENTS = 4, _("Investments")
    OUTING = 5, _("Outing")
    UTILITIES = 6, _("Utilities")
    COMPANY = 7, _("Company")
    PPF = 8, _("PPF")
    MISCELLANEOUS = 9, _("Miscellaneous")
    HOME_LOAN = 10, _("Home Loan")
    CREDIT_CARDS = 11, _("Credit Cards")
    CAR_LOAN = 12, _("Car Loan")
    PERSONAL_LOAN = 13, _("Personal Loan")
    GENERAL = 14, _("General")
    LEASE_ACCOUNT = 15, _("Lease Account")
    FIXED_DEPOSIT = 16, _("Fixed Deposit")
    RECURSIVE_DEPOSIT = 17, _("Recursive Deposit")
    INSURANCES = 18, _("Insurances")
    HEALTH_INSURANCE = 19, _("Health Insurance")
    TERM_INSURANCE = 20, _("Term Insurance")
    LIFE_INSURANCE = 21, _("Life Insurance")
    ACCIDENT_COVER = 22, _("Accident Cover")
    EPF = 23, _("EPF")
    SAVING_ACCOUNT = 24, _("Saving Account")
    CURRENT_ACCOUNT = 25, _("Current Account")
    CREDIT_CARD = 26, _("Credit Card")
    CASH_IN_WALLET = 27, _("Cash In Wallet")
    POLICY_INVESTMENT = 28, _("Policy Investment")
    SUKANYA_SAMRIDDHI_ACCOUNT = 29, _("Sukanya Samriddhi Account")
    MUTUAL_FUNDS = 30, _("Mutual Funds")
    NPS = 31, _("NPS")
    STOCKS = 32, _("Stocks")
    GOLD = 33, _("Gold")
    TRADING_ACCOUNT = 34, _("Trading Account")
    DEMAT_ACCOUNT = 35, _("Demat Account")
