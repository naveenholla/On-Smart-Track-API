import pandas as pd
import talib as ta
from django.db import transaction

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.holidays import HolidayData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.data.index_equity import PullEquityIndexData
from ontrack.market.models.lookup import (
    Equity,
    EquityIndex,
    Exchange,
    Index,
    MarketDay,
    MarketDayCategory,
    MarketDayType,
)
from ontrack.utils.base.enum import AdminSettingKey as sk
from ontrack.utils.base.fixtures import FixtureData
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.context import application_context
from ontrack.utils.logger import ApplicationLogger
from ontrack.utils.numbers import NumberHelper as nh
from ontrack.utils.ta.identify_candlestick import recognize_candlestick


class MarketLookupData(BaseLogic):
    def __init__(self, exchange_symbol):
        self.logger = ApplicationLogger()
        self.settings = SettingLogic()
        self.fixtureData = FixtureData()

        exchange_qs = Exchange.backend.get_queryset()
        self.exchange = exchange_qs.unique_search(exchange_symbol).first()
        self.equity_dict = None
        self.index_dict = None
        self.equityindex_dict = None

        if not self.exchange:
            return

        self.daytype_qs = MarketDayType.backend.get_queryset()
        self.category_qs = MarketDayCategory.backend.get_queryset()
        self.day_qs = MarketDay.backend.get_queryset()
        self.holiday_obj = HolidayData(
            self.exchange, self.daytype_qs, self.category_qs, self.day_qs
        )

    def populate_equity_dict(self):
        if not self.equity_dict or len(self.equity_dict) == 0:
            equity_qs = Equity.backend.get_queryset()
            self.equity_dict = self.create_dict(equity_qs)

            self.pull_equity_obj = PullEquityData(self.exchange, self.equity_dict)

    def populate_index_dict(self):
        if not self.index_dict or len(self.index_dict) == 0:
            index_qs = Index.backend.get_queryset()
            self.index_dict = self.create_dict(index_qs, "name")

            self.pull_index_obj = PullIndexData(self.exchange, self.index_dict)

    def populate_equity_index_dict(self):
        self.populate_equity_dict()
        self.populate_index_dict()
        if not self.equityindex_dict or len(self.equityindex_dict) == 0:
            equityindex_qs = EquityIndex.backend.get_queryset()
            self.equityindex_dict = self.create_dict(equityindex_qs, "equity_index")

            self.pull_equity_index_obj = PullEquityIndexData(
                self.exchange, self.equity_dict, self.index_dict, self.equityindex_dict
            )

    def load_fixtures_all_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
            "market.marketday",
            "market.equity",
            "market.index",
            "market.equityindex",
        ]

        self.fixtureData.load_fixtures_data(fixtures, temp_folder_path)

    def load_fixtures_data(self, temp_folder_path=None):
        fixtures = [
            "market.exchange",
            "market.marketdaytype",
            "market.marketdaycategory",
            "market.marketday",
        ]

        self.fixtureData.load_fixtures_data(fixtures, temp_folder_path)

    def load_equity_data(self):
        self.populate_equity_dict()
        result = self.pull_equity_obj.pull_and_parse_lookup_data()
        self.equity_dict = None
        return result

    def load_index_data(self):
        self.populate_index_dict()
        result = self.pull_index_obj.pull_and_parse_lookup_data()
        self.index_dict = None
        return result

    def pull_indices_market_cap(self, record):
        self.populate_equity_index_dict()
        result = self.pull_equity_index_obj.pull_indices_market_cap(record)
        return result

    def parse_indices_market_cap(self, index_name, record):
        self.populate_equity_index_dict()
        result = self.pull_equity_index_obj.parse_indices_market_cap(index_name, record)
        return result

    def load_equity_index_data(self):
        self.populate_equity_index_dict()
        result = self.pull_equity_index_obj.pull_and_parse_market_cap()
        self.equityindex_dict = None
        return result

    def load_holidays_data(self):
        return self.holiday_obj.pull_parse_exchange_holidays()

    def execute_market_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange):
            date_key = sk.DATAPULL_EQUITY_LOOKUP_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EQUITY_LOOKUP_PAUSE_HOURS
            cet = self.can_execute_task(date_key, pause_hour_key)
            if not cet[0]:
                message = cet[1]
                self.logger.log_info(message)
                return message

            try:
                result_equity = self.load_equity_data()
                result_index = self.load_index_data()
                result_equity_index = self.load_equity_index_data()
                with transaction.atomic():
                    records_stats = self.create_or_update(result_equity, Equity)
                    output.append(self.message_creator("Equity", records_stats))

                    records_stats = self.create_or_update(result_index, Index)
                    output.append(self.message_creator("Index", records_stats))

                    records_stats = self.create_or_update(
                        result_equity_index, EquityIndex
                    )
                    output.append(self.message_creator("Equity Index", records_stats))
            except Exception as e:
                message = f"Exception - `{format(e)}`."
                self.logger.log_critical(message=message)
                output.append(self.message_creator("Lookup Data", message))

            key = sk.LOOKUP_DATA_OLDER_THAN_DAYS_CAN_BE_DELETED
            days_count = nh.str_to_float(self.settings.get_by_key(key))
            EquityIndex.backend.delete_old_records(days_count)

            self.settings.save_task_execution_time(date_key)

        return output

    def calculated_eod_data(self):
        self.populate_equity_dict()
        # days_count = nh.str_to_float(self.settings.get_by_key(sk.NO_OF_DAYS_AVG))

        equities = ["hdfcbank"]

        for equity in self.equity_dict.values():
            if equity.symbol.lower() in equities:
                eod_data = equity.eod_data.order_by("date").all()
                # df = pd.DataFrame(list(eod_data.values("date","prev_close",
                # "open_price", "high_price", "low_price", "last_price",
                # "close_price", "avg_price", "delivery_quantity",
                # "delivery_percentage", "percentage_changed",
                # "quantity_per_trade", "point_changed")))
                # df["point_changed2"] = df["close_price"].diff()
                # df["quantity_per_trade_avg"] = df["quantity_per_trade"].rolling(window=20).mean()

                df1 = pd.DataFrame(
                    list(
                        eod_data.values(
                            "date",
                            "open_price",
                            "high_price",
                            "low_price",
                            "close_price",
                        )
                    )
                )
                df1.rename(
                    columns={
                        "open_price": "open",
                        "high_price": "high",
                        "low_price": "low",
                        "close_price": "close",
                    },
                    inplace=True,
                )

                df1["date"] = pd.to_datetime(
                    df1["date"],
                    format="%Y-%m-%d %H:%M:%S.%f %z",
                    errors="coerce",
                    utc=True,
                )
                df1["date"] = df1["date"].dt.tz_convert("Asia/Kolkata")
                df1["MA5_mean"] = (
                    ta.MA(df1["close"], timeperiod=5)
                    / ta.MA(df1["close"], timeperiod=5).mean()
                )
                df1["MA5"] = ta.MA(df1["close"], timeperiod=5)

                with pd.option_context(
                    "display.max_rows",
                    None,
                    "display.max_columns",
                    None,
                    "display.width",
                    None,
                ):
                    df1 = recognize_candlestick(df1)
                    print(df1)

                # df = pd.DataFrame(
                #     list(
                #         eod_data.values(
                #             "date",
                #             "close_price",
                #             "delivery_quantity",
                #             "traded_quantity",
                #             "percentage_changed",
                #             "quantity_per_trade",
                #             "delivery_percentage",
                #         )
                #     )
                # )
                # df["point_changed2"] = df["close_price"].diff()
                # df["average_quantity_per_trade"] = (
                #     df["quantity_per_trade"].rolling(window=20).mean()
                # )
                # df["average_average_volumn"] = (
                #     df["traded_quantity"].rolling(window=20).mean()
                # )
                # df["average_delivery_percentage"] = (
                #     df["delivery_percentage"].rolling(window=20).mean()
                # )
                # df["per_delivery_percentage"] = (
                #     df["delivery_percentage"].astype(float)
                #     / df["average_delivery_percentage"]
                # )
                # df["per_average_volumn"] = (
                #     df["traded_quantity"].astype(float) / df["average_average_volumn"]
                # )
                # df["per_quantity_per_trade"] = (
                #     df["quantity_per_trade"].astype(float)
                #     / df["average_quantity_per_trade"]
                # )
                # df["MA_10"] = ta.EMA(df["close_price"], timeperiod=10)

                # print(ta.get_functions())

                # with pd.option_context(
                #     "display.max_rows",
                #     None,
                #     "display.max_columns",
                #     None,
                #     "display.width",
                #     None,
                # ):
                #     print(
                #         df[
                #             [
                #                 "date",
                #                 "per_average_volumn",
                #                 "per_delivery_percentage",
                #                 "per_quantity_per_trade",
                #                 "MA_10",
                #             ]
                #         ]
                #     )

                # ta["MA5"] = tb.MA(c, timeperiod=5) / tb.MA(c, timeperiod=5).mean()
                # ta["MA10"] = tb.MA(c, timeperiod=10) / tb.MA(c, timeperiod=10).mean()
                # ta["MA20"] = tb.MA(c, timeperiod=20) / tb.MA(c, timeperiod=20).mean()
                # ta["MA60"] = tb.MA(c, timeperiod=60) / tb.MA(c, timeperiod=60).mean()
                # ta["MA120"] = tb.MA(c, timeperiod=120) / tb.MA(c, timeperiod=120).mean()
                # ta["MA5"] = tb.MA(v, timeperiod=5) / tb.MA(v, timeperiod=5).mean()
                # ta["MA10"] = tb.MA(v, timeperiod=10) / tb.MA(v, timeperiod=10).mean()
                # ta["MA20"] = tb.MA(v, timeperiod=20) / tb.MA(v, timeperiod=20).mean()
                # ta["ADX"] = (
                #     tb.ADX(h, l, c, timeperiod=14)
                #     / tb.ADX(h, l, c, timeperiod=14).mean()
                # )
                # ta["ADXR"] = (
                #     tb.ADXR(h, l, c, timeperiod=14)
                #     / tb.ADXR(h, l, c, timeperiod=14).mean()
                # )
                # ta["MACD"] = (
                #     tb.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)[0]
                #     / tb.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)[0].mean()
                # )
                # ta["RSI"] = tb.RSI(c, timeperiod=14) / tb.RSI(c, timeperiod=14).mean()
                # ta["BBANDS_U"] = (
                #     tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[0]
                #     / tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[
                #         0
                #     ].mean()
                # )
                # ta["BBANDS_M"] = (
                #     tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[1]
                #     / tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[
                #         1
                #     ].mean()
                # )
                # ta["BBANDS_L"] = (
                #     tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[2]
                #     / tb.BBANDS(c, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)[
                #         2
                #     ].mean()
                # )
                # ta["AD"] = tb.AD(h, l, c, v) / tb.AD(h, l, c, v).mean()
                # ta["ATR"] = (
                #     tb.ATR(h, l, c, timeperiod=14)
                #     / tb.ATR(h, l, c, timeperiod=14).mean()
                # )
                # ta["HT_DC"] = tb.HT_DCPERIOD(c) / tb.HT_DCPERIOD(c).mean()
                # ta["High/Open"] = h / o
                # ta["Low/Open"] = l / o
                # ta["Close/Open"] = c / o

    def execute_holidays_lookup_data_task(self):
        output = []
        with application_context(exchange=self.exchange):
            date_key = sk.DATAPULL_HOLIDAYS_LOOKUP_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_HOLIDAYS_LOOKUP_PAUSE_HOURS
            cet = self.can_execute_task(date_key, pause_hour_key)
            if not cet[0]:
                message = cet[1]
                self.logger.log_info(message)
                return message

            result = self.load_holidays_data()
            records_stats = self.create_or_update(result, MarketDay)
            output.append(self.message_creator("Holidays", records_stats))

            self.settings.save_task_execution_time(date_key)

        return output
