import math


class NumberHelper:
    @staticmethod
    def roundOff(price, digits=2) -> float:  # Round off to 2 decimal places
        return round(price, digits)

    @staticmethod
    def round_to_market_Price(price) -> float:
        # this will convert 2.33 -> 2.35

        x = round(price, 2) * 20
        y = math.ceil(x)
        return y / 20

    @staticmethod
    def get_nearest_strike_price(price, strikeDifference) -> float:
        if isinstance(strikeDifference, int):
            price = int(price)
            remainder = int(price % strikeDifference)
            center = int(strikeDifference / 2)
        else:
            remainder = price % strikeDifference
            center = strikeDifference / 2

        if remainder < center:
            value = price - remainder
        else:
            value = price + (strikeDifference - remainder)

        return NumberHelper.round_to_market_Price(value)

    @staticmethod
    def get_upper_lower_limit(price, strikeDifference, record_limit) -> float:
        price = NumberHelper.get_nearest_strike_price(price, strikeDifference)

        return price - (strikeDifference * (record_limit - 1)), price + (
            strikeDifference * (record_limit - 1)
        )

    @staticmethod
    def str_to_float(value) -> float:
        if value is None:
            return 0.00

        if isinstance(value, float):
            return value

        value = str(value).strip()

        if value == "-" or value.lower() == "nil" or value == "":
            return 0.00

        return float(value)

    @staticmethod
    def ceil(value: float) -> float:
        if value is None:
            return 0.00

        return math.ceil(value)
