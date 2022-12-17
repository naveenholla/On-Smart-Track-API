import json

import pandas as pd
from django.conf import settings

import ontrack.trading.base  # noqa F401
from ontrack.trading.base.handler import BaseHandler
from ontrack.users.models.lookup import DematAccount
from ontrack.utils.base.enum import DematAccountAccessType
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.obj import obj


class AccountLogic(BaseLogic):
    def __init__(self, user, recorder=None):
        tp = TaskProgressStatus(recorder)
        self.tp = tp

        self.user = user

    def validate_demat_account_login(self, account):
        if account["account_type"] == DematAccountAccessType.VIRTUAL:
            return True

        if account["access_token"] is not None:
            return True

        return False

    def get_demat_account_handler(self, account):
        for cls in BaseHandler.__subclasses__():
            institute = account["institute_name"]
            clientid = account["client_id"]
            if settings.PORT:
                host_name = f"http://{settings.DOMAIN_NAME}:{settings.PORT}"
            else:
                host_name = f"http://{settings.DOMAIN_NAME}"

            config = {}
            config["institute_name"] = institute
            config["clientId"] = clientid
            config["appKey"] = account["app_key"]
            config["appSecret"] = account["app_secret"]
            config["accessToken"] = None
            config[
                "redirectUrl"
            ] = f"{host_name}/api/trading/{institute.lower()}/{clientid}/"

            if cls.brokerName == account["institute_name"]:
                return cls(None, obj(config))

        return None

    def get_demat_account_login_url(self, account):
        handler = self.get_demat_account_handler(account)
        if handler:
            return handler.get_login_url()

        return None

    def get_all_demat_accounts(self):
        accounts = DematAccount.backend.filter(account__user_id=self.user.id)
        df = pd.DataFrame(
            list(
                accounts.values(
                    "id",
                    "account__name",
                    "institute__name",
                    "account_type",
                    "client_id",
                    "app_key",
                    "app_secret",
                    "access_token",
                    "is_login_initated",
                    "is_active",
                    "last_login",
                    "Funds",
                    "available_cash",
                    "margin",
                )
            )
        )

        common_names = {
            "account__name": "account_name",
            "institute__name": "institute_name",
        }
        df.rename(columns=common_names, errors="ignore", inplace=True)
        df["is_connected"] = df.apply(
            lambda row: self.validate_demat_account_login(row), axis=1
        )
        df["redirect_url"] = df.apply(
            lambda row: self.get_demat_account_login_url(row), axis=1
        )
        df.drop(["app_key", "app_secret", "access_token"], axis=1, inplace=True)

        return json.loads(df.to_json(orient="records"))
