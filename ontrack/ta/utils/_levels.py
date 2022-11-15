import datetime as dt

import numpy as np
from pandas import Timestamp


def _create_level_object(row, type):
    level = {}
    level["type"] = type
    level["open"] = row["open"]
    level["high"] = row["high"]
    level["low"] = row["low"]
    level["close"] = row["close"]
    return level


def _current_previous_levels(df, type):
    levels = []

    level = _create_level_object(df[-1], f"current {type}")
    levels.append(level)

    level = _create_level_object(df[-2], f"previous {type}")
    levels.append(level)

    return levels


def monthly_levels(df):
    df_values = df.resample("M").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return _current_previous_levels(df_values, "month")


def weekly_levels(df):
    df_values = df.resample("W").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return _current_previous_levels(df_values, "week")


def firty_two_week_levels(df):
    df_values = df.rolling(window=252, center=False).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return _create_level_object(df_values[-1], "52 week")


def _support(df, index, n1, n2):
    # n1 n2 before and after candle index
    for i in range(index - n1 + 1, index + 1):
        if df["Low"][i] > df["Low"][i - 1]:
            return False

    for i in range(index + 1, index + n2 + 1):
        if df["Low"][i] < df["Low"][i - 1]:
            return False
    return True


def _resistance(df, index, n1, n2):
    # n1 n2 before and after candle index
    for i in range(index - n1 + 1, index + 1):
        if df["High"][i] < df["High"][i - 1]:
            return False

    for i in range(index + 1, index + n2 + 1):
        if df["High"][i] > df["High"][i - 1]:
            return False
    return True


# method 1: fractal candlestick pattern
# determine bullish fractal
def _is_support(df, i):
    cond1 = df["Low"][i] < df["Low"][i - 1]
    cond2 = df["Low"][i] < df["Low"][i + 1]
    cond3 = df["Low"][i + 1] < df["Low"][i + 2]
    cond4 = df["Low"][i - 1] < df["Low"][i - 2]
    return cond1 and cond2 and cond3 and cond4


# determine bearish fractal
def _is_resistance(df, i):
    cond1 = df["High"][i] > df["High"][i - 1]
    cond2 = df["High"][i] > df["High"][i + 1]
    cond3 = df["High"][i + 1] > df["High"][i + 2]
    cond4 = df["High"][i - 1] > df["High"][i - 2]
    return cond1 and cond2 and cond3 and cond4


# to make sure the new level area does not exist already
def _is_far_from_level(value, levels, df):
    ave = np.mean(df["High"] - df["Low"])
    return np.sum([abs(value - level) < ave for _, level in levels]) == 0


# method 1: fractal candlestick pattern
def _fractal_candlestick_pattern_sr(df):
    levels = []
    indexes = list(df.index.values)
    for i in range(2, df.shape[0] - 2):
        index = Timestamp(indexes[i])
        if _is_support(df, i):
            l = df["Low"][i]
            if _is_far_from_level(l, levels, df):
                levels.append((index, l))
        elif _is_resistance(df, i):
            l = df["High"][i]
            if _is_far_from_level(l, levels, df):
                levels.append((index, l))
    return levels


def fractal_candlestick_pattern_sr_2(df, n1=2, n2=2):
    levels = []
    indexes = list(df.index.values)
    for i in range(2, df.shape[0] - 2):
        index = Timestamp(indexes[i])
        if _support(df, i, n1, n2):
            l = df["Low"][i]
            if _is_far_from_level(l, levels, df):
                levels.append((index, l))
        elif _resistance(df, i, n1, n2):
            l = df["High"][i]
            if _is_far_from_level(l, levels, df):
                levels.append((index, l))
    return levels


# method 2: window shifting method
def window_shifting_method_sr(df, window=5):
    levels = []
    max_list = []
    min_list = []
    for i in range(window, len(df) - window):
        high_range = df["High"][i - window : i + window - 1]
        current_max = high_range.max()
        if current_max not in max_list:
            max_list = []
        max_list.append(current_max)
        if len(max_list) == window and _is_far_from_level(current_max, levels, df):
            levels.append((high_range.idxmax(), current_max))

        low_range = df["Low"][i - window : i + window]
        current_min = low_range.min()
        if current_min not in min_list:
            min_list = []
        min_list.append(current_min)
        if len(min_list) == window and _is_far_from_level(current_min, levels, df):
            levels.append((low_range.idxmin(), current_min))
    return levels


def get_support_resistance(df, n1=2, n2=2, window=5):
    # n1 n2 before and after candle index
    all_pivots_dict = []
    levels = fractal_candlestick_pattern_sr_2(df, n1, n2)
    for level in levels:
        point = np.round(level[1], 2)

        pivot = {}
        pivot["type"] = "SR - fractal candlestick pattern"
        pivot["date"] = level[0].to_pydatetime()
        pivot["level"] = point
        all_pivots_dict.append(pivot)

    levels = window_shifting_method_sr(df, window)
    for level in levels:
        point = np.round(level[1], 2)

        pivot = {}
        pivot["type"] = "SR - window shifting method"
        pivot["date"] = level[0].to_pydatetime()
        pivot["level"] = point
        all_pivots_dict.append(pivot)

    return all_pivots_dict
