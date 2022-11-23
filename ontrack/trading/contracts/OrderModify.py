class OrderModify:
    def __init__(self):
        self.newPrice = 0
        self.newTriggerPrice = 0  # Applicable in case of SL order
        self.newQty = 0
        self.newOrderType = None  # Ex: Can change LIMIT order to SL order or vice versa. Not supported by all brokers

    def __str__(self):
        return (
            f"newPrice={self.newPrice}, "
            f"newTriggerPrice={self.newTriggerPrice}, "
            f"newQty={self.newQty}, "
            f"newOrderType={self.newOrderType}"
        )
