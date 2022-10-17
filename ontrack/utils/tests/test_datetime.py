from datetime import datetime, time, timedelta

import pytest
import pytz
from freezegun import freeze_time

from ontrack.utils.datetime import DateTimeHelper

utcTimeZone = pytz.timezone("UTC")
test_year = 2021
test_month = 6
test_date = 20
test_week = 1
test_hour = 6
test_minute = 52
test_second = 12
test_millisecond = 500
test_timezone = utcTimeZone
test_datetime = datetime(
    test_year,
    test_month,
    test_date,
    test_hour,
    test_minute,
    test_second,
    test_millisecond,
    tzinfo=test_timezone,
)

test_datetime_2 = datetime(
    test_year + 1,
    test_month + 1,
    test_date + 1,
    test_hour + 1,
    test_minute + 1,
    test_second + 1,
    test_millisecond + 1,
    tzinfo=test_timezone,
)

test_date_obj = datetime(
    test_year,
    test_month,
    test_date,
    tzinfo=test_timezone,
)

test_time = time(
    test_hour,
    test_minute,
    test_second,
    test_millisecond,
    tzinfo=test_timezone,
)


@freeze_time(test_datetime)
def test_current_date_freeze_time():
    date_obj = DateTimeHelper.current_date_time()
    assert date_obj == test_datetime


@freeze_time(test_datetime)
def test_current_date():
    date_obj = DateTimeHelper.current_date()
    assert date_obj == test_date_obj


@freeze_time(test_datetime)
def test_current_time():
    time_obj = DateTimeHelper.current_time()
    assert time_obj == test_time


@pytest.mark.parametrize(
    "input_time_obj",
    [None, test_datetime_2],
    ids=["to Current Date", "to Specific Date"],
)
@pytest.mark.parametrize(
    "args",
    [
        {"weeks": test_week},
        {"days": test_date},
        {"hours": test_hour},
        {"minutes": test_minute},
        {"seconds": test_second},
        {"milliseconds": test_millisecond},
        {"microseconds": test_millisecond},
    ],
    ids=[
        "Week(s)",
        "Day(s)",
        "Hour(s)",
        "Minute(s)",
        "Second(s)",
        "Millisecond(s)",
        "Microsecond(s)",
    ],
)
@pytest.mark.parametrize("is_future", [True, False], ids=["Add", "Substract"])
def test_get_future_past_date_week(args, input_time_obj, is_future):
    with freeze_time(test_datetime):
        if input_time_obj is None:
            input_time_obj = test_datetime
        else:
            assert input_time_obj != test_datetime

        if is_future:
            result = DateTimeHelper.get_future_date(date=input_time_obj, **args)
            expected = input_time_obj + timedelta(**args)
        else:
            result = DateTimeHelper.get_past_date(date=input_time_obj, **args)
            expected = input_time_obj - timedelta(**args)

        assert result == expected


def test_set_time_to_date():
    pass
