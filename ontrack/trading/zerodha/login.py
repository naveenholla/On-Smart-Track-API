from kiteconnect import KiteConnect

from ontrack.trading.base.login import BaseLogin
from ontrack.utils.logger import ApplicationLogger


class ZerodhaLogin(BaseLogin):
    def __init__(self, brokerAppDetails):
        self.logger = ApplicationLogger()
        BaseLogin.__init__(self, brokerAppDetails)

    def login(self, args, redirect_url):
        self.logger.log_info("==> ZerodhaLogin .args => %s", args)

        brokerHandle = KiteConnect(api_key=self.brokerAppDetails.appKey)
        redirectUrl = None
        if "request_token" in args:
            requestToken = args["request_token"]
            self.logger.log_info("Zerodha requestToken = %s", requestToken)
            session = brokerHandle.generate_session(
                requestToken, api_secret=self.brokerAppDetails.appSecret
            )

            accessToken = session["access_token"]
            accessToken = accessToken
            self.logger.log_info("Zerodha accessToken = %s", accessToken)
            brokerHandle.set_access_token(accessToken)

            self.logger.log_info(
                "Zerodha Login successful. accessToken = %s", accessToken
            )

            # set broker handle and access token to the instance
            self.setBrokerHandle(brokerHandle)
            self.setAccessToken(accessToken)

            # redirect to home page with query param loggedIn=true
            homeUrl = redirect_url + "?loggedIn=true"
            self.logger.log_info("Zerodha Redirecting to home page %s", homeUrl)
            redirectUrl = homeUrl
        else:
            loginUrl = brokerHandle.login_url()
            self.logger.log_info("Redirecting to zerodha login url = %s", loginUrl)
            redirectUrl = loginUrl

        return redirectUrl
