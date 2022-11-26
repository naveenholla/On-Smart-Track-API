class BaseHandler:
    def __init__(self):
        pass

    # Derived class should implement login function and return redirect url
    def get_login_url(self):
        return self.get_broker_login_url()

    def set_access_token(self, args):
        self.accessToken = self.set_broker_access_token(self, args)
        # TODO: Save Access Token

    def get_handler(self):
        return self.get_broker_handler()

    def get_funds(self):
        return self.get_broker_funds()
