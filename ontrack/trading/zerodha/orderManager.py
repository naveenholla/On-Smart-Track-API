import logging

from ontrack.trading.base.orderManager import BaseOrderManager
from ontrack.trading.contracts.Order import Order
from ontrack.utils.base.enum import (
    DirectionType,
    OrderStatusType,
    OrderType,
    OrderValidityType,
)
from ontrack.utils.datetime import DateTimeHelper


class ZerodhaOrderManager(BaseOrderManager):
    def __init__(self):
        super().__init__("zerodha")

    def placeOrder(self, orderInputParams):
        self.logger.log_info(
            "%s: Going to place order with params %s", self.broker, orderInputParams
        )
        kite = self.brokerHandle
        try:
            exchange = (
                kite.EXCHANGE_NFO if orderInputParams.isFnO else kite.EXCHANGE_NSE
            )
            orderId = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=orderInputParams.tradingSymbol,
                transaction_type=self.convertToBrokerDirection(
                    orderInputParams.direction
                ),
                quantity=orderInputParams.qty,
                price=orderInputParams.price,
                trigger_price=orderInputParams.triggerPrice,
                product=self.convertToBrokerProductType(orderInputParams.productType),
                order_type=self.convertToBrokerOrderType(orderInputParams.orderType),
            )

            self.logger.log_info(
                "%s: Order placed successfully, orderId = %s", self.broker, orderId
            )
            order = Order(orderInputParams)
            order.orderId = orderId
            order.orderPlaceTimestamp = DateTimeHelper.__get_epoch()
            order.lastOrderUpdateTimestamp = DateTimeHelper.__get_epoch()
            return order
        except Exception as e:
            self.logger.log_info("%s Order placement failed: %s", self.broker, str(e))
            raise Exception(str(e))

    def modifyOrder(self, order, orderModifyParams):
        self.logger.log_info(
            "%s: Going to modify order with params %s", self.broker, orderModifyParams
        )
        kite = self.brokerHandle
        try:
            orderId = kite.modify_order(
                variety=kite.VARIETY_REGULAR,
                order_id=order.orderId,
                quantity=orderModifyParams.newQty
                if orderModifyParams.newQty > 0
                else None,
                price=orderModifyParams.newPrice
                if orderModifyParams.newPrice > 0
                else None,
                trigger_price=orderModifyParams.newTriggerPrice
                if orderModifyParams.newTriggerPrice > 0
                else None,
                order_type=orderModifyParams.newOrderType,
            )

            self.logger.log_info(
                "%s Order modified successfully for orderId = %s", self.broker, orderId
            )
            order.lastOrderUpdateTimestamp = DateTimeHelper.__get_epoch()
            return order
        except Exception as e:
            self.logger.log_info("%s Order modify failed: %s", self.broker, str(e))
            raise Exception(str(e))

    def modifyOrderToMarket(self, order):
        self.logger.log_info("%s: Going to modify order with params %s", self.broker)
        kite = self.brokerHandle
        try:
            orderId = kite.modify_order(
                variety=kite.VARIETY_REGULAR,
                order_id=order.orderId,
                order_type=kite.ORDER_TYPE_MARKET,
            )

            self.logger.log_info(
                "%s Order modified successfully to MARKET for orderId = %s",
                self.broker,
                orderId,
            )
            order.lastOrderUpdateTimestamp = DateTimeHelper.__get_epoch()
            return order
        except Exception as e:
            self.logger.log_info(
                "%s Order modify to market failed: %s", self.broker, str(e)
            )
            raise Exception(str(e))

    def cancelOrder(self, order):
        self.logger.log_info("%s Going to cancel order %s", self.broker, order.orderId)
        kite = self.brokerHandle
        try:
            orderId = kite.cancel_order(
                variety=kite.VARIETY_REGULAR, order_id=order.orderId
            )

            self.logger.log_info(
                "%s Order cancelled successfully, orderId = %s", self.broker, orderId
            )
            order.lastOrderUpdateTimestamp = DateTimeHelper.__get_epoch()
            return order
        except Exception as e:
            self.logger.log_info("%s Order cancel failed: %s", self.broker, str(e))
            raise Exception(str(e))

    def fetchAndUpdateAllOrderDetails(self, orders):
        self.logger.log_info("%s Going to fetch order book", self.broker)
        kite = self.brokerHandle
        orderBook = None
        try:
            orderBook = kite.orders()
        except Exception as e:
            logging.error("%s Failed to fetch order book %s", self.broker, str(e))
            return

        self.logger.log_info("%s Order book length = %d", self.broker, len(orderBook))
        numOrdersUpdated = 0
        for bOrder in orderBook:
            foundOrder = None
            for order in orders:
                if order.orderId == bOrder["order_id"]:
                    foundOrder = order
                    break

            if foundOrder is not None:
                self.logger.log_info("Found order for orderId %s", foundOrder.orderId)
                foundOrder.qty = bOrder["quantity"]
                foundOrder.filledQty = bOrder["filled_quantity"]
                foundOrder.pendingQty = bOrder["pending_quantity"]
                foundOrder.orderStatus = bOrder["status"]
                if (
                    foundOrder.orderStatus == OrderStatusType.CANCELLED
                    and foundOrder.filledQty > 0
                ):
                    # Consider this case as completed in our system as we cancel the
                    # order with pending qty when strategy stop timestamp reaches
                    foundOrder.orderStatus = OrderStatusType.COMPLETED
                foundOrder.price = bOrder["price"]
                foundOrder.triggerPrice = bOrder["trigger_price"]
                foundOrder.averagePrice = bOrder["average_price"]
                self.logger.log_info("%s Updated order %s", self.broker, foundOrder)
                numOrdersUpdated += 1

        self.logger.log_info(
            "%s: %d orders updated with broker order details",
            self.broker,
            numOrdersUpdated,
        )

    def convertToBrokerProductType(self, productType):
        kite = self.brokerHandle
        if productType == OrderValidityType.MIS:
            return kite.PRODUCT_MIS
        elif productType == OrderValidityType.NRML:
            return kite.PRODUCT_NRML
        elif productType == OrderValidityType.CNC:
            return kite.PRODUCT_CNC
        return None

    def convertToBrokerOrderType(self, orderType):
        kite = self.brokerHandle
        if orderType == OrderType.LIMIT:
            return kite.ORDER_TYPE_LIMIT
        elif orderType == OrderType.MARKET:
            return kite.ORDER_TYPE_MARKET
        elif orderType == OrderType.SL_MARKET:
            return kite.ORDER_TYPE_SLM
        elif orderType == OrderType.SL_LIMIT:
            return kite.ORDER_TYPE_SL
        return None

    def convertToBrokerDirection(self, direction):
        kite = self.brokerHandle
        if direction == DirectionType.LONG:
            return kite.TRANSACTION_TYPE_BUY
        elif direction == DirectionType.SHORT:
            return kite.TRANSACTION_TYPE_SELL
        return None
