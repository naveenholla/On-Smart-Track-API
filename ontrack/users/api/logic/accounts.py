import json

import pandas as pd

from ontrack.users.models.lookup import DematAccount
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus


class AccountLogic(BaseLogic):
    def __init__(self, user, recorder=None):
        tp = TaskProgressStatus(recorder)
        self.tp = tp

        self.user = user

    def get_all_demat_accounts(self):
        accounts = DematAccount.backend.filter(account__user_id=self.user.id)
        df = pd.DataFrame(
            list(
                accounts.values(
                    "account__name",
                    "institute__name",
                    "account_type",
                    "client_id",
                    "is_login_initated",
                    "is_active",
                    "last_login",
                )
            )
        )

        common_names = {
            "account__name": "account_name",
            "institute__name": "institute_name",
        }
        df.rename(columns=common_names, errors="ignore", inplace=True)

        return json.loads(df.to_json(orient="records"))
