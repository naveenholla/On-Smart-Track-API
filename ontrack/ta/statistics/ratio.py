import numpy as np

from ontrack.ta.utils import get_offset, verify_series


def ratio(close, length=None, offset=None, **kwargs):
    """Indicator: Ratio"""
    # Validate Arguments
    length = int(length) if length and length > 0 else 20
    min_periods = (
        int(kwargs["min_periods"])
        if "min_periods" in kwargs and kwargs["min_periods"] is not None
        else length
    )
    close = verify_series(close, max(length, min_periods))
    offset = get_offset(offset)

    if close is None:
        return

    close = close.astype(float)

    # Calculate Result
    mean = close.rolling(length, min_periods=min_periods).mean()
    ratio = np.round(close / mean, 2)

    # Offset
    if offset != 0:
        ratio = ratio.shift(offset)

    # Handle fills
    if "fillna" in kwargs:
        ratio.fillna(kwargs["fillna"], inplace=True)
    if "fill_method" in kwargs:
        ratio.fillna(method=kwargs["fill_method"], inplace=True)

    # Name & Category
    ratio.name = f"RATIO_{length}"
    ratio.category = "statistics"

    return ratio


ratio.__doc__ = """Rolling Ratio

Rolling Ratio of over 'n' periods. Sibling of a Simple Moving Average.

Sources:
    https://www.incrediblecharts.com/indicators/ratio_price.php

Calculation:
    Default Inputs:
        length=30
    mean = close.rolling(length).mean()
    ratio = close / mean

Args:
    close (pd.Series): Series of 'close's
    length (int): It's period. Default: 30
    offset (int): How many periods to offset the result. Default: 0

Kwargs:
    fillna (value, optional): pd.DataFrame.fillna(value)
    fill_method (value, optional): Type of fill method

Returns:
    pd.Series: New feature generated.
"""
