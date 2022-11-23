from ontrack.utils.base.enum import BrokerSegmentType, OrderValidityType


class OrderInput:
    def __init__(self, tradingSymbol):
        self.exchange = "NSE"  # default
        self.isFnO = False
        self.segment = BrokerSegmentType.EQUITY  # default
        self.productType = OrderValidityType.MIS  # default
        self.tradingSymbol = tradingSymbol
        self.direction = ""
        self.orderType = ""  # One of the values of ordermgmt.OrderType
        self.qty = 0
        self.price = 0
        self.triggerPrice = 0  # Applicable in case of SL order

    def __str__(self):
        return (
            f"symbol={self.tradingSymbol}, "
            f"exchange={self.exchange}, "
            f"productType={self.productType}, "
            f"segment={self.segment}, "
            f"direction={self.direction}, "
            f"orderType={self.orderType}, "
            f"price={self.price}, "
            f"triggerPrice={self.triggerPrice}, "
            f"isFnO={self.isFnO}"
        )
