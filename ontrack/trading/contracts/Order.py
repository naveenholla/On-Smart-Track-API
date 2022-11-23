class Order:
    def __init__(self, orderInputParams=None):
        self.tradingSymbol = orderInputParams.tradingSymbol if orderInputParams else ""
        self.exchange = orderInputParams.exchange if orderInputParams else "NSE"
        self.productType = orderInputParams.productType if orderInputParams else ""

        # LIMIT/MARKET/SL-LIMIT/SL-MARKET
        self.orderType = orderInputParams.orderType if orderInputParams else ""
        self.price = orderInputParams.price if orderInputParams else 0

        # Applicable in case of SL orders
        self.triggerPrice = orderInputParams.triggerPrice if orderInputParams else 0
        self.qty = orderInputParams.qty if orderInputParams else 0
        # The order id received from broker after placing the order
        self.orderId = None

        # One of the status defined in ordermgmt.OrderStatus
        self.orderStatus = None

        # Average price at which the order is filled
        self.averagePrice = 0

        # Filled quantity
        self.filledQty = 0

        # Qty - Filled quantity
        self.pendingQty = 0

        # Timestamp when the order is placed
        self.orderPlaceTimestamp = None

        # Applicable if you modify the order Ex: Trailing SL
        self.lastOrderUpdateTimestamp = None

        # In case any order rejection or any other error save the response from broker in this field
        self.message = None

    def __str__(self):
        return (
            f"orderId={self.orderId}, "
            f"orderStatus={self.orderStatus}, "
            f"tradingSymbol={self.tradingSymbol}, "
            f"exchange={self.exchange}, "
            f"productType={self.productType}, "
            f"orderType={self.orderType}, "
            f"price={self.price}, "
            f"triggerPrice={self.triggerPrice}, "
            f"qty={self.qty}, "
            f"pendingQty={self.pendingQty}, "
            f"filledQty={self.filledQty}, "
            f"averagePrice={self.averagePrice}, "
            f"orderPlaceTimestamp={self.orderPlaceTimestamp}, "
            f"lastOrderUpdateTimestamp={self.lastOrderUpdateTimestamp}, "
            f"message={self.message}"
        )
