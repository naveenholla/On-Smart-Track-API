from datetime import timedelta

import pytest
from freezegun import freeze_time

from ontrack.utils.datetime import DateTimeHelper as dt

time_zone = "UTC"
test_year = 2021
test_month = 6
test_date = 20
test_week = 1
test_hour = 6
test_minute = 52
test_second = 12
test_datetime = dt.get_date_time(
    test_year,
    test_month,
    test_date,
    test_hour,
    test_minute,
    test_second,
    time_zone=time_zone,
)

test_datetime_2 = dt.get_date_time(
    test_year + 1,
    test_month + 1,
    test_date + 1,
    test_hour + 1,
    test_minute + 1,
    test_second + 1,
    time_zone=time_zone,
)

test_date_obj = dt.get_date_time(
    test_year,
    test_month,
    test_date,
    time_zone=time_zone,
)

test_time = test_datetime.time()


@pytest.mark.unittest
@freeze_time(test_datetime)
def test_current_date_freeze_time():
    date_obj = dt.current_date_time()
    assert date_obj == test_datetime


@pytest.mark.unittest
@freeze_time(test_datetime)
def test_current_date():
    date_obj = dt.current_date()
    assert date_obj == test_date_obj


@pytest.mark.unittest
@freeze_time(test_datetime)
def test_current_time():
    time_obj = dt.current_time()
    assert time_obj == test_time


@pytest.mark.unittest
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
    ],
    ids=[
        "Week(s)",
        "Day(s)",
        "Hour(s)",
        "Minute(s)",
        "Second(s)",
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
            result = dt.get_future_date(date=input_time_obj, **args)
            expected = input_time_obj + timedelta(**args)
        else:
            result = dt.get_past_date(date=input_time_obj, **args)
            expected = input_time_obj - timedelta(**args)

        assert result == expected


@pytest.mark.unittest
@pytest.mark.parametrize(
    "time_zone,expected_hour,expected_minute",
    [("UTC", 10, 1), ("US/Pacific", 17, 1), ("Asia/Kolkata", 4, 31)],
)
@pytest.mark.parametrize(
    "input_time_obj",
    [None, test_datetime_2],
    ids=["Current Date", "Specific Date"],
)
def test_set_time_to_date(input_time_obj, time_zone, expected_hour, expected_minute):
    with freeze_time(test_datetime):
        if input_time_obj is None:
            input_time_obj = test_datetime
        else:
            assert input_time_obj != test_datetime

        d = dt.set_time_to_date(
            hours=10,
            minutes=1,
            seconds=3,
            time_zone=time_zone,
            dateTimeObj=input_time_obj,
        )
        assert d.tzinfo == input_time_obj.tzinfo

        assert d.hour == expected_hour
        assert d.minute == expected_minute
        assert d.second == 3


@pytest.mark.unittest
@pytest.mark.parametrize(
    "datetimeStr, dateFormat, time_zone, expected",
    [
        (None, None, None, None),
        (test_datetime, None, None, test_datetime),
        ("-", None, None, None),
        ("NIL", None, None, None),
        ("    ", None, None, None),
        ("2022-10-20", "%Y-%m-%d", None, dt.get_date_time(2022, 10, 20)),
        (
            "2022-10-20",
            "%Y-%m-%d",
            "UTC",
            dt.get_date_time(2022, 10, 20, time_zone="UTC"),
        ),
    ],
)
def test_str_to_datetime(datetimeStr, dateFormat, time_zone, expected):
    value = dt.str_to_datetime(datetimeStr, dateFormat, time_zone)
    assert value == expected


@pytest.mark.unittest
@pytest.mark.parametrize(
    "datetimeStr, dateFormat, expected",
    [
        (test_datetime, None, test_datetime.strftime("%Y-%m-%d %H:%M:%S.%f %z")),
        (test_datetime, "%Y-%m-%d", test_datetime.strftime("%Y-%m-%d")),
        (test_datetime, "%Y-%b-%d", test_datetime.strftime("%Y-%b-%d")),
    ],
)
def test_datetime_to_str(datetimeStr, dateFormat, expected):
    value = dt.datetime_to_str(datetimeStr, dateFormat)
    assert value == expected
