from pandas import DataFrame

from ontrack.ta.utils import get_offset, verify_series


def cpr(open_, high, low, close, offset=None, **kwargs):
    """Indicator: cpr"""
    # Validate Arguments
    open_ = verify_series(open_)
    high = verify_series(high)
    low = verify_series(low)
    close = verify_series(close)
    offset = get_offset(offset)

    # Calculate Result
    bc = (high + low) / 2
    pivot = (high + close + low) / 3
    tc = (pivot - bc) + pivot

    r3 = high + (2 * (pivot - low))
    r2 = pivot + (high - low)
    r1 = (2 * pivot) - low

    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - (2 * (high - pivot))

    cpr = abs((tc - pivot) * 2)

    # Offset
    if offset != 0:
        tc = tc.shift(offset)
        pivot = pivot.shift(offset)
        bc = bc.shift(offset)

        r3 = r3.shift(offset)
        r2 = r2.shift(offset)
        r1 = r1.shift(offset)

        s3 = s3.shift(offset)
        s2 = s2.shift(offset)
        s1 = s1.shift(offset)

        cpr = cpr.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        tc.fillna(kwargs["fillna"], inplace=True)
        pivot.fillna(kwargs["fillna"], inplace=True)
        bc.fillna(kwargs["fillna"], inplace=True)

        r3.fillna(kwargs["fillna"], inplace=True)
        r2.fillna(kwargs["fillna"], inplace=True)
        r1.fillna(kwargs["fillna"], inplace=True)

        s3.fillna(kwargs["fillna"], inplace=True)
        s2.fillna(kwargs["fillna"], inplace=True)
        s1.fillna(kwargs["fillna"], inplace=True)

        cpr.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        tc.fillna(method=kwargs["fill_method"], inplace=True)
        pivot.fillna(method=kwargs["fill_method"], inplace=True)
        bc.fillna(method=kwargs["fill_method"], inplace=True)

        r3.fillna(method=kwargs["fill_method"], inplace=True)
        r2.fillna(method=kwargs["fill_method"], inplace=True)
        r1.fillna(method=kwargs["fill_method"], inplace=True)

        s3.fillna(method=kwargs["fill_method"], inplace=True)
        s2.fillna(method=kwargs["fill_method"], inplace=True)
        s1.fillna(method=kwargs["fill_method"], inplace=True)

        cpr.fillna(method=kwargs["fill_method"], inplace=True)

    # Name and Categorize it
    tc.name = f"CPR_TC"
    pivot.name = f"CPR_PIVOT"
    bc.name = f"CPR_BC"

    r3.name = f"CPR_R3"
    r2.name = f"CPR_R2"
    r1.name = f"CPR_R1"

    s3.name = f"CPR_S3"
    s2.name = f"CPR_S2"
    s1.name = f"CPR_S1"

    cpr.name = f"CPR"

    cpr.category = "volatility"
    tc.category = pivot.category = bc.category = cpr.category
    r3.category = r2.category = r1.category = cpr.category
    s3.category = s2.category = s1.category = cpr.category

    # Prepare DataFrame to return
    data = {
        tc.name: tc,
        pivot.name: pivot,
        bc.name: bc,
        r3.name: r3,
        r2.name: r2,
        r1.name: r1,
        s3.name: s3,
        s2.name: s2,
        s1.name: s1,
        cpr.name: cpr,
    }
    cprdf = DataFrame(data)
    cprdf.name = f"CPR"
    cprdf.category = cpr.category

    return cprdf


cpr.__doc__ = """Central Pivot Range (CPR)

Central Pivot Range as mentioned above is a tool for technical analysis. Traders use it in intraday trading as an efficient trading indicator. Central Pivot Range (CPR) indicator is used to identify key points of price levels and trade accordingly. Traders can take up trading positions based on the different levels on the chart. It is quite popular among traders as it is quite versatile and simple to understand. CPR indicator has three levels that are pointed on the chart. These levels are pivot points, top central pivot point, and bottom central pivot point.

Calculation:
    Pivot point = (High + Low + Close) / 3
    Top Central Pivot Point (BC) = (Pivot - BC) + Pivot
    Bottom Central Pivot Point (TC) = (High + Low) / 2

    R3, R2, R1 = Resistance Levels
    S3, S2, S1 = Support Levels

    r3 = high + (2 * (pivot - low))
    r2 = pivot + (high - low)
    r1 = (2 * pivot) - low

    s1 = (2 * pivot) - high
    s2 = pivot - (high - low)
    s3 = low - (2 * (high - pivot))

    cpr = abs((((high + low) / 2) - pivot) * 2)

Args:
    open (pd.Series): Series of 'open's
    high (pd.Series): Series of 'high's
    low (pd.Series): Series of 'low's
    close (pd.Series): Series of 'close's
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.DataFrame: tc, pivot, bc, r3, r2, r1, s1, s2, s3, and cpr columns.
"""
