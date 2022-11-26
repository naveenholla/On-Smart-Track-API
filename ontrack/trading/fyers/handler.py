from django.conf import settings

from ontrack.packages.fyers_api import accessToken, fyersModel
from ontrack.trading.base.handler import BaseHandler
from ontrack.utils.logger import ApplicationLogger


class BrokerHandler(BaseHandler):
    def __init__(self, brokerConfig, accountConfig):
        self.logger = ApplicationLogger()

        self.brokerName = "Fyers"
        self.brokerConfig = brokerConfig
        self.accountConfig = accountConfig
        self.clientId = self.accountConfig.clientId
        self.appKey = self.accountConfig.appKey
        self.appSecret = self.accountConfig.appSecret
        self.accessToken = self.accountConfig.accessToken
        self.redirectUrl = self.accountConfig.redirectUrl
        self.log_folder = settings.LOGS_DIR / self.brokerName

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
        session = accessToken.SessionModel(
            client_id=self.client_id,
            secret_key=self.appSecret,
            redirect_uri=self.redirectUrl,
            response_type=self.responseType,
            grant_type=self.grantType,
            state=self.state,
            scope=self.scope,
            nonce=self.nonce,
        )
        session.set_token(auth_code)
        return session

    def get_broker_handler(self):
        handler = fyersModel.FyersModel(
            is_async=self.is_async,
            client_id=self.clientId,
            token=self.accessToken,
            log_path=self.log_folder,
        )
        return handler

    def get_broker_login_url(self):
        session = self.session()
        loginUrl = session.generate_authcode()
        self.logger.log_info(f"{self.brokerName} login url = {loginUrl}")
        return loginUrl

    def get_broker_access_token(self, args):
        self.logger.log_info(
            f"Getting {self.brokerName} access token with args => {args}"
        )
        if "auth_code" in args:
            auth_code = args["auth_code"]
            self.logger.log_info(f"{self.brokerName} auth_code = {auth_code}")

            session = self.__get_session(auth_code)
            response = session.generate_token()

            accessToken = response["access_token"]
            self.logger.log_info(
                f"{self.brokerName} Login successful. accessToken = {accessToken}"
            )

            return accessToken

    def get_broker_funds(self):
        handler = self.get_broker_handler()
        return handler.funds()

        # Available Margin = Cash + liquid_collateral + stock_collateral
        # Cash
        # liquid_collateral
        # stock_collateral
        # opening_balance
        # intraday_payin
        # payout
        # Span
        # Delivery Margin
        # Exposure
        # Option Premium
        # turnover
        # holding_sales
        # m2m_unrealised
        # m2m_realised
        # debits


#      {
#    "s": "ok",
#    "code": 200,
#    "message": "",
#    "fund_limit":
#                [{
#                  "id":9,
#                  "title":"Limit at start of the day",
#                  "equityAmount":-132253.4,
#                  "commodityAmount": -37393.81
#                },
#                {
#                  "id":8,
#                  "title":"Adhoc Limit",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                },
#                {
#                  "id":7,
#                  "title":"Receivables",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                },
#                {
#                  "id":6,
#                  "title":"Fund Transfer",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "100000.0"
#                },
#                {
#                  "id":5,
#                  "title":"Collaterals",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                },
#                {
#                  "id":4,
#                  "title":"Realized Profit and Loss",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                },
#                {
#                  "id":2,
#                  "title":"Utilized Amount",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                },
#                {
#                  "id":3,
#                  "title":"Clear Balance",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                },
#                {
#                  "id":3,
#                  "title":"Clear Balance",
#                  "equityAmount": "0.0",
#                  "commodityAmount": 62606.19
#                },
#                {
#                  "id":1,
#                  "title":"Total Balance",
#                  "equityAmount": -132253.4,
#                  "commodityAmount": 62606.19
#                },
#                {
#                  "id":10,
#                  "title":"Available Balance",
#                  "equityAmount": -132253.4,
#                  "commodityAmount": 62606.19
#                },
#                {
#                  "id":11,
#                  "title":"Available Balance",
#                  "equityAmount": "A",
#                  "commodityAmount": "M"
#                },
#                {
#                  "id":12,
#                  "title":"Available Balance",
#                  "equityAmount": "0.0",
#                  "commodityAmount": "0.0"
#                }]
#  }
