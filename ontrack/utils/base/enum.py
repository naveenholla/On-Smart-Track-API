from django.db import models


class AdminSettingKey(models.TextChoices):
    NO_OF_DAYS_AVG = "NO_OF_DAYS_AVG"
    DATAPULL_EQUITY_LOOKUP_DATE = "DATAPULL_EQUITY_LOOKUP_DATE"
    DATAPULL_EQUITY_LOOKUP_DAY_PAUSE = "DATAPULL_EQUITY_LOOKUP_DAY_PAUSE"
    DATAPULL_EQUITY_EOD_DATA_DATE = "DATAPULL_EQUITY_EOD_DATA_DATE"
    DATAPULL_INDICES_EOD_DATA_DATE = "DATAPULL_INDICES_EOD_DATA_DATE"


class UserSettingKey(models.TextChoices):
    DEFAULT_THEME = "DEFAULT_THEME"
    DEFAULT_LANGUAGE = "DEFAULT_LANGUAGE"
    DEFAULT_CURRENCY = "DEFAULT_CURRENCY"
    DEFAULT_DATE_FORMAT = "DEFAULT_DATE_FORMAT"
    NOTIFICATION_ENABLED = "NOTIFICATION_ENABLED"


class ExpiryType(models.TextChoices):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class OrderValidityType(models.TextChoices):
    MIS = "MIS"
    NRML = "NRML"
    CNC = "CNC"


class MarketDayTypeEnum(models.TextChoices):
    TRADING_HOLIDAY = "Trading Holiday"
    CLEARING_HOLIDAY = "Clearing Holiday"
    WEEKLY_OFF_DAYS = "Weekly Off Days"
    SPECIAL_TRADING_DAY = "Special Trading Day"


class HolidayParentCategoryType(models.TextChoices):
    CAPITAL_MARKET = "Capital Market"
    DEBT_MARKET = "Debt Market"
    DERIVATIVES_MARKET = "Derivatives Market"


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
    RETAIL = "RETAIL"


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
    LONG = "LONG"
    SHORT = "SHORT"


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
