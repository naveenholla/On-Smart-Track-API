import calendar
import logging
import time
from datetime import date, datetime, timedelta

from dateutil import tz
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from .config import Configurations
from .context import get_context_value_by_key
from .logger import ApplicationLogger


class DateTimeHelper:
    logger = ApplicationLogger()

    @staticmethod
    def current_date_time() -> datetime:
        return timezone.now()

    @staticmethod
    def current_date() -> datetime:
        return DateTimeHelper.current_date_time().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    @staticmethod
    def current_time():
        return DateTimeHelper.current_date_time().timetz()

    @staticmethod
    def get_date_time(year, month, day, hour=0, minute=0, second=0, time_zone=None):
        if time_zone is None:
            time_zone = "Asia/Kolkata"

        t = tz.gettz(time_zone)
        d = datetime(year, month, day, hour, minute, second)
        d = d.replace(tzinfo=t)
        return d

    @staticmethod
    def get_future_date(
        date=None,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        milliseconds=0,
        microseconds=0,
    ) -> datetime:
        if date is None:
            date = DateTimeHelper.current_date_time()

        time_threshold = date + timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
        )
        return time_threshold

    @staticmethod
    def get_past_date(
        date=None,
        weeks=0,
        days=0,
        hours=0,
        minutes=0,
        seconds=0,
        milliseconds=0,
        microseconds=0,
    ) -> datetime:
        if date is None:
            date = DateTimeHelper.current_date_time()

        time_threshold = date - timedelta(
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            microseconds=microseconds,
            milliseconds=milliseconds,
        )
        return time_threshold

    @staticmethod
    def set_time_to_date(hours, minutes, seconds, time_zone, dateTimeObj=None):
        if dateTimeObj is None:
            dateTimeObj = DateTimeHelper.current_date_time()
        from_zone = dateTimeObj.tzinfo
        to_zone = tz.gettz(time_zone)
        dateTimeObj = dateTimeObj.replace(tzinfo=to_zone)
        dateTimeObj = dateTimeObj.replace(hour=hours, minute=minutes, second=seconds)
        dateTimeObj = dateTimeObj.astimezone(from_zone)
        return dateTimeObj

    @staticmethod
    def set_time_to_current_date(hours, minutes, seconds, time_zone):
        return DateTimeHelper.set_time_to_date(
            hours, minutes, seconds, time_zone, DateTimeHelper.current_date_time()
        )

    @staticmethod
    def datetime_to_str(datetimeObj: datetime, dateFormat: str = None) -> str:
        f = Configurations.get_default_value_by_key("default_date_time_format")
        if dateFormat is not None and len(dateFormat) > 0:
            f = dateFormat
        return datetimeObj.strftime(f)

    @staticmethod
    def str_to_datetime(datetimeStr, dateFormat=None, time_zone=None) -> datetime:
        if datetimeStr is None:
            return None

        if time_zone is None:
            time_zone = "Asia/Kolkata"

        if isinstance(datetimeStr, datetime):
            return datetimeStr

        datetimeStr = str(datetimeStr).strip()

        if datetimeStr == "-" or datetimeStr.lower() == "nil" or datetimeStr == "":
            return None

        f = Configurations.get_default_value_by_key("default_date_time_format")
        if dateFormat is not None and len(dateFormat) > 0:
            f = dateFormat

        t = tz.gettz(time_zone)
        d = datetime.strptime(datetimeStr, f)
        d = d.replace(tzinfo=t)
        return d

    @staticmethod
    def str_to_time(timeStr: str, timeFormat: str = None) -> time.struct_time:
        f = Configurations.get_default_value_by_key("default_time_format")
        if timeFormat is not None and len(timeFormat) > 0:
            f = timeFormat
        return time.strptime(timeStr, f)

    @staticmethod
    def get_today_date_string(dateFormat: str) -> str:
        return DateTimeHelper.datetime_to_str(
            DateTimeHelper.current_date_time(), dateFormat
        )

    @staticmethod
    def get_exchange_object():
        exchangeObj = get_context_value_by_key("exchange")
        return exchangeObj

    @staticmethod
    def get_exchange_off_days():
        exchangeObj = DateTimeHelper.get_exchange_object()
        return exchangeObj.get

    @staticmethod
    def is_holiday(datetimeObj: date) -> bool:
        exchange_name = get_context_value_by_key("exchange_name")
        holiday_category_name = get_context_value_by_key("holiday_category_name")
        holiday_day_type = get_context_value_by_key("holiday_day_type")

        special_trading_days = Configurations.get_exchange_special_days(
            exchange_name=exchange_name
        )
        weekly_off_days = Configurations.get_exchange_weekly_off(
            exchange_name=exchange_name
        )
        holidays = Configurations.get_exchange_days_by_type(
            exchange_name=exchange_name,
            day_type_name=holiday_day_type,
            category_name=holiday_category_name,
        )

        dateStr = DateTimeHelper.datetime_to_str(datetimeObj, "%Y-%m-%d")
        dayOfWeek = calendar.day_name[datetimeObj.weekday()]

        if special_trading_days:
            special_day = [
                x for x in special_trading_days if x["date"] and x["date"] == dateStr
            ]
            if special_day and len(special_day) > 0:
                return False

        if weekly_off_days:
            weekly_off = [
                x
                for x in weekly_off_days
                if x["day"] and str(x["day"]).lower() == dayOfWeek.lower()
            ]
            if weekly_off and len(weekly_off) > 0:
                return True

        holiday = [x for x in holidays if x["date"] and x["date"] == dateStr]
        return holiday and len(holiday) > 0

    @staticmethod
    def is_holiday_today() -> bool:
        return DateTimeHelper.is_holiday(DateTimeHelper.current_date_time())

    @staticmethod
    def set_market_time(time_key, dateTimeObj=None) -> datetime:
        exchangeObj = DateTimeHelper.get_exchange_object()
        time_value = DateTimeHelper.str_to_time(exchangeObj[time_key])
        timezone = exchangeObj["time_zone"]["zone"]
        return DateTimeHelper.set_time_to_date(
            time_value.tm_hour,
            time_value.tm_min,
            time_value.tm_sec,
            time_zone=timezone,
            dateTimeObj=dateTimeObj,
        )

    @staticmethod
    def get_market_start_time(dateTimeObj=None) -> datetime:
        return DateTimeHelper.set_market_time(
            time_key="start_time", dateTimeObj=dateTimeObj
        )

    @staticmethod
    def get_market_end_time(dateTimeObj=None) -> datetime:
        return DateTimeHelper.set_market_time(
            time_key="end_time", dateTimeObj=dateTimeObj
        )

    @staticmethod
    def get_market_refresh_time(dateTimeObj=None) -> datetime:
        return DateTimeHelper.set_market_time(
            time_key="data_refresh_time", dateTimeObj=dateTimeObj
        )

    @staticmethod
    def remove_time(dateTimeObj=None) -> datetime:
        exchangeObj = DateTimeHelper.get_exchange_object()
        timezone = exchangeObj["time_zone"]["zone"]
        return DateTimeHelper.set_time_to_date(
            0, 0, 0, time_zone=timezone, dateTimeObj=dateTimeObj
        )

    @staticmethod
    def is_data_refreshed(dateTimeObj=None):
        if dateTimeObj is None:
            dateTimeObj = DateTimeHelper.current_date_time()

        market_refresh_time = DateTimeHelper.get_market_refresh_time(dateTimeObj)
        now = DateTimeHelper.current_date_time()
        DateTimeHelper.logger.log_debug(
            f"market_refresh_time:{market_refresh_time}, dateTimeObj:{dateTimeObj}, cuurent_time: {now}"
        )
        return now >= market_refresh_time

    @staticmethod
    def is_market_open() -> bool:
        if DateTimeHelper.is_holiday_today():
            return False

        now = DateTimeHelper.current_date_time()
        marketStartTime = DateTimeHelper.get_market_start_time()
        marketEndTime = DateTimeHelper.get_market_end_time()
        return now >= marketStartTime and now <= marketEndTime

    @staticmethod
    def is_market_close_for_the_day() -> bool:
        # This method returns true if the current time is > marketEndTime
        # Please note this will not return true if current time is < marketStartTime on a trading day
        if DateTimeHelper.is_holiday_today():
            return True

        now = DateTimeHelper.current_date_time()
        marketEndTime = DateTimeHelper.get_market_end_time()
        return now > marketEndTime

    @staticmethod
    def get_epoch(datetimeObj=None) -> int:
        # This method converts given datetimeObj to epoch seconds
        if datetimeObj is None:
            datetimeObj = DateTimeHelper.current_date_time()
        epochSeconds = datetime.timestamp(datetimeObj)
        return int(epochSeconds)  # converting double to long

    @staticmethod
    def wait_time_till_market_opens():
        nowEpoch = DateTimeHelper.get_epoch(DateTimeHelper.current_date_time())
        marketStartTimeEpoch = DateTimeHelper.get_epoch(
            DateTimeHelper.get_market_start_time()
        )
        waitSeconds = marketStartTimeEpoch - nowEpoch
        return waitSeconds

    @staticmethod
    def get_monthly_expiry_day_date(datetimeObj=None, index=0) -> datetime:
        if datetimeObj is None:
            datetimeObj = DateTimeHelper.current_date_time()

        if index > 0:
            datetimeObj = datetimeObj + relativedelta(months=index)

        year = datetimeObj.year
        month = datetimeObj.month
        lastDay = calendar.monthrange(year, month)[
            1
        ]  # 2nd entry is the last day of the month
        datetimeExpiryDay = datetime(year, month, lastDay)

        while calendar.day_name[datetimeExpiryDay.weekday()] != "Thursday":
            datetimeExpiryDay = datetimeExpiryDay - timedelta(days=1)

        while DateTimeHelper.is_holiday(datetimeExpiryDay):
            datetimeExpiryDay = datetimeExpiryDay - timedelta(days=1)

        datetimeExpiryDay = DateTimeHelper.remove_time(dateTimeObj=datetimeExpiryDay)

        expiryDateMarketEndTime = DateTimeHelper.get_market_end_time(datetimeExpiryDay)
        now = DateTimeHelper.current_date_time()
        if now > expiryDateMarketEndTime:
            # as this month expiry is already over get next month expiry
            datetimeExpiryDay = DateTimeHelper.get_monthly_expiry_day_date(
                datetimeObj, index + 1
            )

        return datetimeExpiryDay

    @staticmethod
    def get_weekly_expiry_day_date(dateTimeObj=None, index=0) -> datetime:
        if dateTimeObj is None:
            dateTimeObj = DateTimeHelper.current_date_time()

        if index > 0:
            dateTimeObj = dateTimeObj + relativedelta(weeks=index)

        daysToAdd = 0
        if dateTimeObj.weekday() >= 3:
            daysToAdd = -1 * (dateTimeObj.weekday() - 3)
        else:
            daysToAdd = 3 - dateTimeObj.weekday()

        datetimeExpiryDay = dateTimeObj + timedelta(days=daysToAdd)

        while DateTimeHelper.is_holiday(datetimeExpiryDay):
            datetimeExpiryDay = datetimeExpiryDay - timedelta(days=1)

        datetimeExpiryDay = DateTimeHelper.remove_time(dateTimeObj=datetimeExpiryDay)

        expiryDateMarketEndTime = DateTimeHelper.get_market_end_time(datetimeExpiryDay)
        now = DateTimeHelper.current_date_time()
        if now > expiryDateMarketEndTime:
            datetimeExpiryDay = DateTimeHelper.get_weekly_expiry_day_date(
                dateTimeObj, index + 1
            )

        return datetimeExpiryDay

    @staticmethod
    def prepare_monthly_expiry_futures_symbol(inputSymbol, index=0) -> str:
        expiryDateTime = DateTimeHelper.get_monthly_expiry_day_date(None, index)
        year2Digits = str(expiryDateTime.year)[2:]
        monthShort = calendar.month_name[expiryDateTime.month].upper()[0:3]
        futureSymbol = inputSymbol + year2Digits + monthShort + "FUT"
        logging.info(
            "prepareMonthlyExpiryFuturesSymbol[%s] = %s", inputSymbol, futureSymbol
        )
        return futureSymbol

    @staticmethod
    def prepare_weekly_expiry_options_symbol(
        inputSymbol, strike, optionType, index=0
    ) -> str:
        expiryDateTime = DateTimeHelper.get_weekly_expiry_day_date(None, index)
        expiryDateTimeMonthly = DateTimeHelper.get_monthly_expiry_day_date(None, index)
        # Check if monthly and weekly expiry same
        weekAndMonthExpriySame = False
        if expiryDateTime == expiryDateTimeMonthly:
            weekAndMonthExpriySame = True
            logging.info("Weekly and Monthly expiry is same for %s", expiryDateTime)

        year2Digits = str(expiryDateTime.year)[2:]
        optionSymbol = None
        if weekAndMonthExpriySame:
            monthShort = calendar.month_name[expiryDateTime.month].upper()[0:3]
            optionSymbol = (
                inputSymbol
                + str(year2Digits)
                + monthShort
                + str(strike)
                + optionType.upper()
            )
        else:
            m = expiryDateTime.month
            d = expiryDateTime.day
            mStr = str(m)
            if m == 10:
                mStr = "O"
            elif m == 11:
                mStr = "N"
            elif m == 12:
                mStr = "D"
            dStr = ("0" + str(d)) if d < 10 else str(d)
            optionSymbol = (
                inputSymbol
                + str(year2Digits)
                + mStr
                + dStr
                + str(strike)
                + optionType.upper()
            )
        logging.info(
            "prepareWeeklyOptionsSymbol[%s, %d, %s, %d] = %s",
            inputSymbol,
            strike,
            optionType,
            index,
            optionSymbol,
        )
        return optionSymbol

    @staticmethod
    def prepare_monthly_expiry_options_symbol(
        inputSymbol, strike, optionType, index=0
    ) -> str:
        expiryDateTime = DateTimeHelper.get_monthly_expiry_day_date(None, index)
        year2Digits = str(expiryDateTime.year)[2:]
        monthShort = calendar.month_name[expiryDateTime.month].upper()[0:3]
        optionSymbol = (
            inputSymbol
            + str(year2Digits)
            + monthShort
            + str(strike)
            + optionType.upper()
        )
        logging.info(
            "prepareWeeklyOptionsSymbol[%s, %d, %s, %d] = %s",
            inputSymbol,
            strike,
            optionType,
            index,
            optionSymbol,
        )
        return optionSymbol

    @staticmethod
    def is_today_weekly_expiry_day() -> bool:
        expiryDate = DateTimeHelper.get_weekly_expiry_day_date()
        todayDate = DateTimeHelper.remove_time()
        return expiryDate == todayDate

    @staticmethod
    def days_before_weekly_expiry() -> int:
        expiryDate = DateTimeHelper.get_weekly_expiry_day_date()
        todayDate = DateTimeHelper.remove_time()
        return (expiryDate - todayDate).days
