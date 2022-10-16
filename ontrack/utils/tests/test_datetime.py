from datetime import datetime, time, timedelta

import pytest
import pytz
from freezegun import freeze_time

from ontrack.core.utils.datetime import DateTimeHelper

utcTimeZone = pytz.timezone("UTC")
current_date_year = 2021
current_date_month = 6
current_date_date = 20
current_date_week = 1
current_date_hour = 6
current_date_minute = 52
current_date_second = 12
current_date_millisecond = 500
current_date_timezone = utcTimeZone
current_date_time_value = datetime(
    current_date_year,
    current_date_month,
    current_date_date,
    current_date_hour,
    current_date_minute,
    current_date_second,
    current_date_millisecond,
    tzinfo=current_date_timezone,
)

current_date_time_value_2 = datetime(
    current_date_year + 1,
    current_date_month + 1,
    current_date_date + 1,
    current_date_hour + 1,
    current_date_minute + 1,
    current_date_second + 1,
    current_date_millisecond + 1,
    tzinfo=current_date_timezone,
)

current_date_value = datetime(
    current_date_year,
    current_date_month,
    current_date_date,
    tzinfo=current_date_timezone,
)

current_time_value = time(
    current_date_hour,
    current_date_minute,
    current_date_second,
    current_date_millisecond,
    tzinfo=current_date_timezone,
)

test_data_future_past_values = [
    ({"weeks": current_date_week}, current_date_time_value, None, True),
    ({"days": current_date_date}, current_date_time_value, None, True),
    ({"hours": current_date_hour}, current_date_time_value, None, True),
    ({"minutes": current_date_minute}, current_date_time_value, None, True),
    ({"seconds": current_date_second}, current_date_time_value, None, True),
    ({"microseconds": current_date_millisecond}, current_date_time_value, None, True),
    ({"milliseconds": current_date_millisecond}, current_date_time_value, None, True),
    ({"weeks": current_date_week}, current_date_time_value, None, False),
    ({"days": current_date_date}, current_date_time_value, None, False),
    ({"hours": current_date_hour}, current_date_time_value, None, False),
    ({"minutes": current_date_minute}, current_date_time_value, None, False),
    ({"seconds": current_date_second}, current_date_time_value, None, False),
    ({"microseconds": current_date_millisecond}, current_date_time_value, None, False),
    ({"milliseconds": current_date_millisecond}, current_date_time_value, None, False),
    (
        {"weeks": current_date_week},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"days": current_date_date},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"hours": current_date_hour},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"minutes": current_date_minute},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"seconds": current_date_second},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"microseconds": current_date_millisecond},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"milliseconds": current_date_millisecond},
        current_date_time_value,
        current_date_time_value_2,
        True,
    ),
    (
        {"weeks": current_date_week},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
    (
        {"days": current_date_date},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
    (
        {"hours": current_date_hour},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
    (
        {"minutes": current_date_minute},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
    (
        {"seconds": current_date_second},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
    (
        {"microseconds": current_date_millisecond},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
    (
        {"milliseconds": current_date_millisecond},
        current_date_time_value,
        current_date_time_value_2,
        False,
    ),
]


@freeze_time(current_date_time_value)
def test_current_date_freeze_time():
    date_obj = DateTimeHelper.current_date_time()
    assert date_obj == current_date_time_value


@freeze_time(current_date_time_value)
def test_current_date():
    date_obj = DateTimeHelper.current_date()
    assert date_obj == current_date_value


@freeze_time(current_date_time_value)
def test_current_time():
    time_obj = DateTimeHelper.current_time()
    assert time_obj == current_time_value


@pytest.mark.parametrize(
    "args, current_time_obj, input_time_obj, is_future", test_data_future_past_values
)
def test_get_future_past_date_week(args, current_time_obj, input_time_obj, is_future):
    with freeze_time(current_time_obj):
        if input_time_obj is None:
            input_time_obj = current_time_obj
        else:
            assert input_time_obj != current_time_obj

        if is_future:
            assert DateTimeHelper.get_future_date(date=input_time_obj, **args) == (
                input_time_obj + timedelta(**args)
            )
        else:
            assert DateTimeHelper.get_past_date(date=input_time_obj, **args) == (
                input_time_obj - timedelta(**args)
            )


def test_set_time_to_date():
    pass
