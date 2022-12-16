import numpy as np
import pandas as pd

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt


class MarketParticipantData(BaseLogic):
    def __init__(self, exchange_symbol: str, recorder=None):
        self.settings = SettingLogic()
        self.marketlookupdata = MarketLookupData(exchange_symbol)

        tp = TaskProgressStatus(recorder)
        self.tp = tp

        self.exchange = self.marketlookupdata.exchange()
        self.basicLogic = BaseLogic()

    def get_fii_stats_activities(self):
        with application_context(exchange=self.exchange):
            d = dt.get_past_date(days=10)
            participants = ParticipantStatsActivity.backend.filter(
                date__gte=d
            ).order_by("date")
            df = pd.DataFrame(
                list(
                    participants.values(
                        "date",
                        "client_type",
                        "instrument",
                        "no_of_contracts_bought",
                        "value_of_contracts_bought",
                        "value_of_contracts_sold",
                        "no_of_contracts_sold",
                        "open_interest",
                    )
                )
            )

            common_names = {
                "client_type": "type",
                "instrument": "instrument",
                "no_of_contracts_bought": "bought",
                "value_of_contracts_bought": "bought_value",
                "no_of_contracts_sold": "sold",
                "value_of_contracts_sold": "sold_value",
                "open_interest": "oi",
            }
            df.rename(columns=common_names, errors="ignore", inplace=True)

            df["balance_contracts"] = df["bought"] - df["sold"]
            df["balance_value"] = df["bought_value"] - df["sold_value"]
            df["net_contracts"] = df.groupby(["type", "instrument"])[
                "balance_contracts"
            ].transform(lambda x: x.diff())
            df["net_value"] = df.groupby(["type", "instrument"])[
                "balance_value"
            ].transform(lambda x: x.diff())
            df["change_oi"] = df.groupby(["type", "instrument"])["oi"].transform(
                lambda x: x.diff()
            )
            df["pcr_contracts"] = (df["bought"] / (df["bought"] + df["sold"])).astype(
                float
            )

            conditions = [
                (df["change_oi"] > 0) & (df["balance_value"] > 0),
                (df["change_oi"] > 0) & (df["balance_value"] < 0),
                (df["change_oi"] < 0) & (df["balance_value"] > 0),
                (df["change_oi"] < 0) & (df["balance_value"] < 0),
            ]
            choices = [
                "LONG BUILDUP",
                "SHORT BUILDUP",
                "SHORT COVERING",
                "LONG UNWINDING",
            ]
            df["position"] = np.select(conditions, choices)

            choices = ["BULLISH", "BEARISH", "BULLISH", "BEARISH"]
            df["direction"] = np.select(conditions, choices)

            df.sort_values(by="date", ascending=False, inplace=True)
            return df

    def get_participant_activities(self):
        with application_context(exchange=self.exchange):
            d = dt.get_past_date(days=10)
            instruments = ["FUTIDX", "OPTIDX", "CASH"]
            client_types = ["CLIENT", "PRO", "DII", "FII"]

            participants = ParticipantActivity.backend.filter(
                date__gte=d, instrument__in=instruments, client_type__in=client_types
            )
            participants = participants.order_by("date", "client_type", "instrument")

            df = pd.DataFrame(
                list(
                    participants.values(
                        "date",
                        "client_type",
                        "instrument",
                        "option_type",
                        "buy_amount",
                        "sell_amount",
                        "net_amount",
                    )
                )
            )
            common_names = {"instrument": "instrument"}

            df.rename(columns=common_names, errors="ignore", inplace=True)
            df_groupby = df.groupby(
                ["client_type", "instrument", "option_type"], dropna=False
            )
            df["long"] = df_groupby["buy_amount"].transform(lambda x: x.diff())
            df["short"] = df_groupby["sell_amount"].transform(lambda x: x.diff())
            df["net"] = df["long"] - df["short"]

            df["lsr"] = self.basicLogic.calculate_ratio(df, "buy_amount", "sell_amount")

            conditions = [
                (df["option_type"] != "PE")
                & (df["long"] > df["short"])
                & (df["long"] + df["short"] > 0),
                (df["option_type"] != "PE")
                & (df["long"] < df["short"])
                & (df["long"] + df["short"] > 0),
                (df["option_type"] != "PE")
                & (df["long"] < df["short"])
                & (df["long"] + df["short"] < 0),
                (df["option_type"] != "PE")
                & (df["long"] > df["short"])
                & (df["long"] + df["short"] < 0),
                (df["option_type"] == "PE")
                & (df["long"] > df["short"])
                & (df["long"] + df["short"] > 0),
                (df["option_type"] == "PE")
                & (df["long"] < df["short"])
                & (df["long"] + df["short"] > 0),
                (df["option_type"] == "PE")
                & (df["long"] < df["short"])
                & (df["long"] + df["short"] < 0),
                (df["option_type"] == "PE")
                & (df["long"] > df["short"])
                & (df["long"] + df["short"] < 0),
            ]
            choices = [
                "LONG BUILDUP",
                "SHORT BUILDUP",
                "LONG UNWINDING",
                "SHORT COVERING",
                "SHORT BUILDUP",
                "LONG BUILDUP",
                "SHORT COVERING",
                "LONG UNWINDING",
            ]
            df["position"] = np.select(conditions, choices, default="NA")

            choices = [
                "BULLISH",
                "BEARISH",
                "BEARISH",
                "BULLISH",
                "BEARISH",
                "BULLISH",
                "BULLISH",
                "BEARISH",
            ]
            df["direction"] = np.select(conditions, choices, default="NA")
            df.sort_values(by=["date", "client_type"], ascending=False, inplace=True)
            return df

    def get_fii_future_index_stats(self):
        df = self.get_fii_stats_activities()
        df = df[df["instrument"] == "FUTIDX"]
        df = df[
            [
                "date",
                "oi",
                "change_oi",
                "balance_value",
                "position",
                "direction",
                "instrument",
            ]
        ]
        return df

    def get_participant_cash(self):
        df = self.get_participant_activities()
        df = df[df["instrument"] == "CASH"]
        df = df[["date", "client_type", "buy_amount", "sell_amount", "net_amount"]]
        return df

    def get_participant_index_future(self):
        df = self.get_participant_activities()
        df = df[df["instrument"] == "FUTIDX"]
        df = df[
            [
                "date",
                "client_type",
                "buy_amount",
                "sell_amount",
                "net_amount",
                "long",
                "short",
                "net",
                "lsr",
                "position",
                "direction",
            ]
        ]
        return df

    def get_participant_index_call(self):
        df = self.get_participant_activities()
        df = df[df["option_type"] == "CE"]
        df = df[
            [
                "date",
                "client_type",
                "buy_amount",
                "sell_amount",
                "net_amount",
                "long",
                "short",
                "net",
                "lsr",
                "position",
                "direction",
            ]
        ]
        return df

    def get_participant_index_put(self):
        df = self.get_participant_activities()
        df = df[df["option_type"] == "PE"]
        df = df[
            [
                "date",
                "client_type",
                "buy_amount",
                "sell_amount",
                "net_amount",
                "long",
                "short",
                "net",
                "lsr",
                "position",
                "direction",
            ]
        ]
        return df

    def get_participant_index_put_call(self):
        df = self.get_participant_activities()
        df = df[df["instrument"] == "OPTIDX"]
        df = df.pivot_table("net_amount", ["date", "client_type"], "option_type")
        df["pcr"] = self.basicLogic.calculate_ratio(df, "PE", "CE")
        df.sort_values(by=["date", "client_type"], ascending=False, inplace=True)
        return df
