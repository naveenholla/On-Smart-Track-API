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
            "symbol="
            + str(self.tradingSymbol)
            + ", exchange="
            + self.exchange
            + ", productType="
            + self.productType
            + ", segment="
            + self.segment
            + ", direction="
            + self.direction
            + ", orderType="
            + self.orderType
            + ", qty="
            + str(self.qty)
            + ", price="
            + str(self.price)
            + ", triggerPrice="
            + str(self.triggerPrice)
            + ", isFnO="
            + str(self.isFnO)
        )
