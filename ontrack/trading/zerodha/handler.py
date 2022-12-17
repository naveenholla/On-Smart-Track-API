from django.conf import settings
from kiteconnect import KiteConnect

from ontrack.trading.base.handler import BaseHandler
from ontrack.utils.logger import ApplicationLogger


class BrokerHandler(BaseHandler):
    brokerName = "Zerodha"

    def __init__(self, brokerConfig, accountConfig):
        self.logger = ApplicationLogger()
        self.brokerConfig = brokerConfig
        self.accountConfig = accountConfig
        self.clientId = self.accountConfig.clientId
        self.appKey = self.accountConfig.appKey
        self.appSecret = self.accountConfig.appSecret
        self.accessToken = self.accountConfig.accessToken
        self.redirectUrl = self.accountConfig.redirectUrl
        self.log_folder = settings.LOGS_DIR / BrokerHandler.brokerName

        # This value must always be “code”
        self.responseType = "code"

        # This value must always be “authorization_code
        self.grantType = "authorization_code"

        # You send a random value. The same value will be returned
        # after successful login to the redirect uri.
        self.state = "onsmarttrack"

        # The value in scope must be openid if being passed.
        # Though this is an optional field
        self.scope = None

        # The value in nonce can be any random string value.
        # This is also an optional field
        self.nonce = None
        self.is_async = False

    def __get_session(self, auth_code):
        handler = self.get_broker_handler()
        session = handler.generate_session(auth_code, api_secret=self.appSecret)
        return session

    def get_broker_handler(self):
        handler = KiteConnect(api_key=self.appKey)
        if self.accessToken:
            handler.set_access_token(self.accessToken)
        return handler

    def get_broker_login_url(self):
        handler = self.get_broker_handler()
        loginUrl = handler.login_url()
        self.logger.log_info(f"{BrokerHandler.brokerName} login url = {loginUrl}")
        return loginUrl

    def get_broker_access_token(self, args):
        self.logger.log_info(
            f"Getting {BrokerHandler.brokerName} access token with args => {args}"
        )
        if "request_token" in args:
            auth_code = args["request_token"]
            self.logger.log_info(f"{BrokerHandler.brokerName} auth_code = {auth_code}")

            response = self.__get_session(auth_code)

            accessToken = response["access_token"]
            self.logger.log_info(
                f"{BrokerHandler.brokerName} Login successful. accessToken = {accessToken}"
            )

            return accessToken

    def get_broker_funds(self):
        handler = self.get_broker_handler()
        return handler.margins()
