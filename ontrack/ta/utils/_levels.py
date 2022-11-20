import datetime as dt
import sys
from operator import itemgetter

import numpy as np
from pandas import Timestamp


def _create_level_object(row, type):
    open_ = row["open"]
    high = row["high"]
    low = row["low"]
    close = row["close"]

    levels = []
    level = {}
    level["type"] = f"{type}_O"
    level["level"] = np.round(open_, 2)
    level["is_support"] = True
    levels.append(level)

    level = {}
    level["type"] = f"{type}_H"
    level["level"] = np.round(high)
    level["is_support"] = False
    levels.append(level)

    level = {}
    level["type"] = f"{type}_L"
    level["level"] = np.round(low)
    level["is_support"] = True
    levels.append(level)

    level = {}
    level["type"] = f"{type}_C"
    level["level"] = np.round(close)
    level["is_support"] = False
    levels.append(level)
    return levels


def _current_previous_levels(df, type):
    levels = []

    level = _create_level_object(df.iloc[-1], f"C_{type}")
    levels.extend(level)

    level = _create_level_object(df.iloc[-2], f"P_{type}")
    levels.extend(level)

    return levels


def monthly_levels(df):
    df_values = df.resample("M").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return _current_previous_levels(df_values, "M")


def weekly_levels(df):
    df_values = df.resample("W").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return _current_previous_levels(df_values, "W")


def daily_levels(df):
    return _current_previous_levels(df, "D")


def firty_two_week_levels(df):
    levels = []
    df["52W H"] = df["high"].rolling(window=252, center=False).max()
    df["52W L"] = df["low"].rolling(window=252, center=False).min()

    level = {}
    level["type"] = f"52W_H"
    level["level"] = np.round(df["52W H"].iloc[-1], 2)
    level["is_support"] = False
    levels.append(level)

    level = {}
    level["type"] = f"52W_L"
    level["level"] = np.round(df["52W L"].iloc[-1], 2)
    level["is_support"] = True
    levels.append(level)

    return levels


def all_time_levels(df):
    levels = []
    df["ATH"] = df["high"].max()
    df["ATC"] = df["close"].max()

    level = {}
    level["type"] = f"ATH"
    level["level"] = np.round(df["ATH"].iloc[-1], 2)
    level["is_support"] = False
    levels.append(level)

    level = {}
    level["type"] = f"ATC"
    level["level"] = np.round(df["ATC"].iloc[-1], 2)
    level["is_support"] = False
    levels.append(level)

    return levels


def _add_indicator_levels(df, type_, is_support=True):
    level = {}
    level["type"] = type_
    level["level"] = np.round(df[type_].iloc[-1], 2)
    level["is_support"] = is_support
    return level


def get_all_indicator_levels(df):
    levels = []

    indicators = [
        "SMA_200",
        "SMA_100",
        "SMA_50",
        "EMA_200",
        "EMA_100",
        "EMA_50",
        "CPR_TC",
        "CPR_PIVOT",
        "CPR_BC",
        "CPR_R3",
        "CPR_R2",
        "CPR_R1",
        "CPR_S3",
        "CPR_S2",
        "CPR_S1",
    ]

    for indicator in indicators:
        if indicator in df.columns:
            levels.append(_add_indicator_levels(df, indicator))

    return levels


def _support(df, index, n1, n2):
    # n1 n2 before and after candle index
    for i in range(index - n1 + 1, index + 1):
        if df["low"][i] > df["low"][i - 1]:
            return False

    for i in range(index + 1, index + n2 + 1):
        if df["low"][i] < df["low"][i - 1]:
            return False
    return True


def _resistance(df, index, n1, n2):
    # n1 n2 before and after candle index
    for i in range(index - n1 + 1, index + 1):
        if df["high"][i] < df["high"][i - 1]:
            return False

    for i in range(index + 1, index + n2 + 1):
        if df["high"][i] > df["high"][i - 1]:
            return False
    return True


# method 1: fractal candlestick pattern
# determine bullish fractal
def _is_support(df, i):
    cond1 = df["low"][i] < df["low"][i - 1]
    cond2 = df["low"][i] < df["low"][i + 1]
    cond3 = df["low"][i + 1] < df["low"][i + 2]
    cond4 = df["low"][i - 1] < df["low"][i - 2]
    return cond1 and cond2 and cond3 and cond4


# determine bearish fractal
def _is_resistance(df, i):
    cond1 = df["high"][i] > df["high"][i - 1]
    cond2 = df["high"][i] > df["high"][i + 1]
    cond3 = df["high"][i + 1] > df["high"][i + 2]
    cond4 = df["high"][i - 1] > df["high"][i - 2]
    return cond1 and cond2 and cond3 and cond4


# to make sure the new level area does not exist already
def _is_far_from_level(value, levels, df):
    # Clean noise in data by discarding a level if it is near another
    # (i.e. if distance to the next level is less than the average candle size for any given day - this will give a rough estimate on volatility)
    ave = np.mean(df["high"] - df["low"])
    return np.sum([abs(value - level) < ave for _, level in levels]) == 0


# This function, given a price value, returns True or False depending on if it is too near to some previously discovered key level.
def _distance_from_mean(mean, level, unique_levels):
    return np.sum([abs(level - y) < mean for y in unique_levels]) == 0


def _group_noise(levels, price, mean):
    unique_levels = []
    previous_number = None

    unique_level = {}
    unique_level["point"] = 0
    unique_level["is_below"] = True
    unique_level["min_point"] = sys.maxsize
    unique_level["max_point"] = 0
    unique_level["levels"] = []
    unique_level["types"] = []
    unique_level["dates"] = []
    unique_level["is_support"] = []
    index = -100
    for l in levels:
        level = l["level"]
        type_ = l["type"]
        date_ = l["date"] if "date" in l else None
        is_support = l["is_support"]
        if not previous_number or abs(level - previous_number) < mean:
            if not previous_number:
                previous_number = level

            min_ = min(level, unique_level["min_point"])
            max_ = max(level, unique_level["max_point"])
            point = max_ if level < price else min_
            unique_level["point"] = point
            unique_level["is_below"] = point < price
            unique_level["min_point"] = min_
            unique_level["max_point"] = max_
            unique_level["levels"].append(level)
            unique_level["types"].append(type_)
            unique_level["dates"].append(date_)
            unique_level["is_support"].append(is_support)

            continue

        unique_levels.append(unique_level)
        previous_number = level

        unique_level = {}
        unique_level["point"] = previous_number
        unique_level["is_below"] = previous_number < price
        unique_level["min_point"] = level
        unique_level["max_point"] = level
        unique_level["levels"] = [
            level,
        ]
        unique_level["types"] = [
            type_,
        ]
        unique_level["dates"] = [
            date_,
        ]
        unique_level["is_support"] = [
            is_support,
        ]

    unique_levels.append(unique_level)
    return unique_levels


def _fractal_candlestick_pattern_sr_2(df, n1=2, n2=2, remove_noise=False):
    levels = []
    indexes = list(df.index.values)
    for i in range(2, df.shape[0] - 2):
        index = Timestamp(indexes[i])
        if _support(df, i, n1, n2):
            l = df["low"][i]
            if not remove_noise or _is_far_from_level(l, levels, df):
                levels.append((index, l, "support"))
        elif _resistance(df, i, n1, n2):
            l = df["high"][i]
            if not remove_noise or _is_far_from_level(l, levels, df):
                levels.append((index, l, "resistance"))
    return levels


# method 2: window shifting method
def _window_shifting_method_sr(df, window=5, remove_noise=False):
    levels = []
    max_list = []
    min_list = []
    for i in range(window, len(df) - window):
        high_range = df["high"][i - window : i + window - 1]
        current_max = high_range.max()
        if current_max not in max_list:
            max_list = []
        max_list.append(current_max)
        if len(max_list) == window and (
            not remove_noise or _is_far_from_level(current_max, levels, df)
        ):
            levels.append((high_range.idxmax(), current_max, "resistance"))

        low_range = df["low"][i - window : i + window]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list) == window and (
            not remove_noise or _is_far_from_level(current_min, levels, df)
        ):
            levels.append((low_range.idxmin(), current_min, "support"))
    return levels


def get_support_resistance(df, n1=2, n2=2, window=5):
    # n1 n2 before and after candle index
    all_pivots_dict = []
    levels = _fractal_candlestick_pattern_sr_2(df, n1, n2)
    for level in levels:
        point = np.round(level[1], 2)

        pivot = {}
        pivot["type"] = "SR_FCP"
        pivot["date"] = level[0].to_pydatetime().strftime("%Y-%m-%dT%H:%M:%S.%f")
        pivot["level"] = point
        pivot["is_support"] = level[2] == "support"
        all_pivots_dict.append(pivot)

    levels = _window_shifting_method_sr(df, window)
    for level in levels:
        point = np.round(level[1], 2)

        pivot = {}
        pivot["type"] = "SR_WSM"
        pivot["date"] = level[0].to_pydatetime().strftime("%Y-%m-%dT%H:%M:%S.%f")
        pivot["level"] = point
        pivot["is_support"] = level[2] == "support"
        all_pivots_dict.append(pivot)

    return all_pivots_dict


def _find_nearest_index(levels, value):
    array = np.asarray(levels)
    idx = (np.abs(levels - value)).argmin()
    return idx


def _shrink_list_index(levels, ltp, items_count=10):
    idx = _find_nearest_index(levels, ltp)

    min_idx = idx - items_count
    max_idx = idx + items_count

    if min_idx < 0:
        min_idx = 0

    if max_idx > len(levels):
        max_idx = len(levels)

    return min_idx, max_idx


def get_eod_sr_levels(df_daily, dfs):
    levels = []

    ml = all_time_levels(df_daily)
    levels.extend(ml)

    ml = firty_two_week_levels(df_daily)
    levels.extend(ml)

    ml = monthly_levels(df_daily)
    levels.extend(ml)

    ml = weekly_levels(df_daily)
    levels.extend(ml)

    ml = get_support_resistance(df_daily)
    levels.extend(ml)

    ml = get_all_indicator_levels(df_daily)
    levels.extend(ml)

    for df in dfs:
        ml = get_support_resistance(df)
        levels.extend(ml)

    return levels


def get_intraday_sr_levels(
    eod_levels, df_daily, dfs, ltp, offset_mean=None, item_count=10
):
    levels = eod_levels

    ml = daily_levels(df_daily)
    levels.extend(ml)

    for df in dfs:
        ml = get_support_resistance(df)
        levels.extend(ml)

    sorted_levels = sorted(levels, key=itemgetter("level"), reverse=False)

    if not offset_mean:
        # Clean noise in data by discarding a level if it is near another
        # (i.e. if distance to the next level is less than the average
        # candle size for any given day - this will give a rough estimate on volatility)
        offset_mean = np.mean(dfs[0]["high"] - dfs[0]["low"])

    unique_levels = _group_noise(sorted_levels, ltp, offset_mean)
    points = [x["point"] for x in unique_levels]
    min_, max_ = _shrink_list_index(points, ltp, item_count)
    return unique_levels[min_:max_]


def analysis_market_structure(levels):
    last_support = sys.maxsize
    last_resistance = 0
    swing_low = 0
    swing_high = 0

    for level in levels:
        value = level["level"]
        if last_support >= value:
            # New Low, so upward swing is no longer valid
            swing_low = 0

        if last_resistance <= value:
            # New High, so downward swing is no longer valid
            swing_high = 0

        if level["is_support"]:
            if last_support < value and swing_low == 0:
                swing_low = last_support
            last_support = value
        else:
            if last_resistance > value and swing_high == 0:
                swing_high = last_resistance
            last_resistance = value

    return last_support, last_resistance, swing_low, swing_high
