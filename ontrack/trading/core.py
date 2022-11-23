from ontrack.trading.contracts.BrokerAppDetails import BrokerAppDetails
from ontrack.trading.login.ZerodhaLogin import ZerodhaLogin
from ontrack.utils.logger import ApplicationLogger


class Controller:
    brokerLogin = None  # static variable
    brokerName = None  # static variable
    logger = ApplicationLogger()

    def handleBrokerLogin(args, config):
        brokerAppDetails = BrokerAppDetails(config["broker"])
        brokerAppDetails.setClientID(config["clientID"])
        brokerAppDetails.setAppKey(config["appKey"])
        brokerAppDetails.setAppSecret(config["appSecret"])

        Controller.logger.log_info(
            "handleBrokerLogin appKey %s", brokerAppDetails.appKey
        )
        Controller.brokerName = brokerAppDetails.broker
        if Controller.brokerName == "zerodha":
            Controller.brokerLogin = ZerodhaLogin(brokerAppDetails)
        # Other brokers - not implemented
        # elif Controller.brokerName == 'fyers':
        # Controller.brokerLogin = FyersLogin(brokerAppDetails)

        redirectUrl = Controller.brokerLogin.login(args)
        return redirectUrl

    def getBrokerLogin():
        return Controller.brokerLogin

    def getBrokerName():
        return Controller.brokerName
