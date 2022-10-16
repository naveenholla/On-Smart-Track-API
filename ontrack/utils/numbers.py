import decimal
import math


class NumberHelper:
    @staticmethod
    def roundOff(price) -> decimal:  # Round off to 2 decimal places
        return round(price, 2)

    @staticmethod
    def roundToMarketPrice(price) -> decimal:
        # this will convert 2.33 -> 2.35

        x = round(price, 2) * 20
        y = math.ceil(x)
        return y / 20

    @staticmethod
    def getNearestStrikePrice(price, nearestMultiple=50) -> decimal:
        inputPrice = int(price)
        remainder = int(inputPrice % nearestMultiple)
        if remainder < int(nearestMultiple / 2):
            return inputPrice - remainder
        else:
            return inputPrice + (nearestMultiple - remainder)

    @staticmethod
    def convert_string_to_float(value):
        if value is None:
            return 0.00

        if isinstance(value, float):
            return value

        value = str(value).strip()

        if value == "-" or value.lower() == "nil" or value == "":
            return 0.00

        return float(value)
