import datetime as dt
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
    levels.append(level)

    level = {}
    level["type"] = f"{type}_H"
    level["level"] = np.round(high)
    levels.append(level)

    level = {}
    level["type"] = f"{type}_L"
    level["level"] = np.round(low)
    levels.append(level)

    level = {}
    level["type"] = f"{type}_C"
    level["level"] = np.round(close)
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
    levels.append(level)

    level = {}
    level["type"] = f"52W_L"
    level["level"] = np.round(df["52W L"].iloc[-1], 2)
    levels.append(level)

    return levels


def all_time_levels(df):
    levels = []
    df["ATH"] = df["high"].max()
    df["ATC"] = df["close"].max()

    level = {}
    level["type"] = f"ATH"
    level["level"] = np.round(df["ATH"].iloc[-1], 2)
    levels.append(level)

    level = {}
    level["type"] = f"ATC"
    level["level"] = np.round(df["ATC"].iloc[-1], 2)
    levels.append(level)

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


def _mark_noise(df, levels, price):
    # Clean noise in data by discarding a level if it is near another
    # (i.e. if distance to the next level is less than the average candle size for any given day - this will give a rough estimate on volatility)
    mean = np.mean(df["high"] - df["low"])

    unique_levels = []
    previous_number = None

    unique_level = {}
    unique_level["point"] = 0
    unique_level["min_point"] = 0
    unique_level["max_point"] = 0
    unique_level["levels"] = []
    unique_level["types"] = []
    unique_level["dates"] = []
    for l in levels:
        level = l["level"]
        type_ = l["type"]
        date_ = l["date"] if "date" in l else None
        if not previous_number or abs(level - previous_number) < mean:
            previous_number = level

            min_ = min(level, unique_level["min_point"])
            max_ = max(level, unique_level["max_point"])
            unique_level["point"] = max_ if level < price else min_
            unique_level["min_point"] = min_
            unique_level["max_point"] = max_
            unique_level["levels"].append(level)
            unique_level["types"].append(type_)
            unique_level["dates"].append(date_)

            continue

        unique_levels.append(unique_level)
        previous_number = level

        unique_level = {}
        unique_level["point"] = previous_number
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

    unique_levels.append(unique_level)
    return unique_levels


# method 1: fractal candlestick pattern
def _fractal_candlestick_pattern_sr(df, remove_noise=False):
    levels = []
    indexes = list(df.index.values)
    for i in range(2, df.shape[0] - 2):
        index = Timestamp(indexes[i])
        if _is_support(df, i):
            l = df["low"][i]
            if not remove_noise or _is_far_from_level(l, levels, df):
                levels.append((index, l))
        elif _is_resistance(df, i):
            l = df["high"][i]
            if not remove_noise or _is_far_from_level(l, levels, df):
                levels.append((index, l))
    return levels


def _fractal_candlestick_pattern_sr_2(df, n1=2, n2=2, remove_noise=False):
    levels = []
    indexes = list(df.index.values)
    for i in range(2, df.shape[0] - 2):
        index = Timestamp(indexes[i])
        if _support(df, i, n1, n2):
            l = df["low"][i]
            if not remove_noise or _is_far_from_level(l, levels, df):
                levels.append((index, l))
        elif _resistance(df, i, n1, n2):
            l = df["high"][i]
            if not remove_noise or _is_far_from_level(l, levels, df):
                levels.append((index, l))
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
            levels.append((high_range.idxmax(), current_max))

        low_range = df["low"][i - window : i + window]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list) == window and (
            not remove_noise or _is_far_from_level(current_min, levels, df)
        ):
            levels.append((low_range.idxmin(), current_min))
    return levels


def _get_support_resistance(df, n1=2, n2=2, window=5):
    # n1 n2 before and after candle index
    all_pivots_dict = []
    levels = _fractal_candlestick_pattern_sr_2(df, n1, n2)
    for level in levels:
        point = np.round(level[1], 2)

        pivot = {}
        pivot["type"] = "SR_FCP"
        pivot["date"] = level[0].to_pydatetime()
        pivot["level"] = point
        all_pivots_dict.append(pivot)

    levels = _window_shifting_method_sr(df, window)
    for level in levels:
        point = np.round(level[1], 2)

        pivot = {}
        pivot["type"] = "SR_WSM"
        pivot["date"] = level[0].to_pydatetime()
        pivot["level"] = point
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


def get_all_support_and_resistance(df_yearly, df_hourly, df_15m, df_5m):
    levels = []

    ml = all_time_levels(df_yearly)
    levels.extend(ml)

    ml = firty_two_week_levels(df_yearly)
    levels.extend(ml)

    ml = monthly_levels(df_yearly)
    levels.extend(ml)

    ml = weekly_levels(df_yearly)
    levels.extend(ml)

    ml = daily_levels(df_yearly)
    levels.extend(ml)

    ml = _get_support_resistance(df_yearly)
    levels.extend(ml)

    if not df_hourly.empty:
        ml = _get_support_resistance(df_hourly)
        levels.extend(ml)

    if not df_15m.empty:
        ml = _get_support_resistance(df_15m)
        levels.extend(ml)

    sorted_levels = sorted(levels, key=itemgetter("level"), reverse=False)

    df_mean = df_yearly
    if not df_hourly.empty:
        df_mean = df_hourly

    if not df_15m.empty:
        df_mean = df_15m

    if not df_5m.empty:
        df_mean = df_5m

    price = df_mean.iloc[-1]["close"]

    unique_levels = _mark_noise(df_mean, sorted_levels, price)

    points = [x["point"] for x in unique_levels]

    min_, max_ = _shrink_list_index(points, price)
    return unique_levels[min_:max_]
