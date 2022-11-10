import json
from operator import itemgetter

import pandas as pd
import talib
from django.db.models import Avg, OuterRef, Prefetch, Subquery
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from ontrack.market.api.logic.endofdata import EndOfDayData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.equity import EquityEndOfDay
from ontrack.market.models.lookup import Equity, EquityIndex
from ontrack.ta.candles.cdl_recognization import recognize_candlestick
from ontrack.utils.base.enum import HolidayCategoryType
from ontrack.utils.base.mixins import SuperAdminPermissionMixin
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.numbers import NumberHelper as nh


class EquityEndOfDayDataTaskAPIView(SuperAdminPermissionMixin, APIView):
    def put(self, request, *args, **kwargs):
        exchange = request.data.get("exchange")
        startdate = dt.str_to_datetime(request.data.get("startdate"), "%Y-%m-%d")
        enddate = dt.str_to_datetime(request.data.get("enddate"), "%Y-%m-%d")

        if not exchange:
            return Response(None)

        obj = EndOfDayData(exchange)
        result = obj.execute_equity_eod_data_task(startdate, enddate)

        return Response(
            data={
                "datetime": dt.current_dt_display_str(),
                "exchange": exchange,
                "result": result,
            }
        )


class StockSelectionAPIView(SuperAdminPermissionMixin, APIView):
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = "market/index.html"

    def get(self, request, *args, **kwargs):
        exchange = request.query_params.get("exchange")
        index = request.query_params.get("symbol")
        date = dt.str_to_datetime(request.query_params.get("date"), "%Y-%m-%d")
        avg_days = nh.str_to_float(request.query_params.get("avg_days"))

        if not exchange:
            return Response(None)

        obj = EndOfDayData(exchange)
        result = obj.stock_selection_hidden_move(date, index, avg_days)

        return Response(result)


class StockSelectionAPIViewReference(SuperAdminPermissionMixin, APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "market/index.html"

    def get(self, request, *args, **kwargs):
        exchange = request.query_params.get("exchange")
        index_symbol = request.query_params.get("symbol")
        date = dt.str_to_datetime(request.query_params.get("date"), "%Y-%m-%d")
        days_count = nh.str_to_float(request.query_params.get("days_count"))

        if not exchange:
            return Response(None)

        exchangeobj = MarketLookupData().populate_exchange(exchange)
        with application_context(
            exchange=exchangeobj,
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            date = dt.get_last_working_day(date)
            print(date)

        if not days_count:
            days_count = 30

        past_date = dt.get_past_date(date, days=days_count)

        equity_eod_data_set = (
            EquityEndOfDay.backend.values("entity_id")
            .filter(date__gte=past_date, date__lt=date)
            .annotate(avg_qpt=Avg("quantity_per_trade") * 2)
        )
        eod_data_latest = EquityEndOfDay.backend.filter(date=date).filter(
            quantity_per_trade__gt=Subquery(
                equity_eod_data_set.filter(entity_id=OuterRef("entity_id")).values(
                    "avg_qpt"
                )[:1]
            )
        )

        queryset = Equity.backend.filter(
            id__in=Subquery(eod_data_latest.values("entity_id"))
        )

        if index_symbol:
            equity_index = EquityIndex.backend.filter(
                index__symbol__iexact=index_symbol
            )
            queryset = queryset.filter(
                id__in=Subquery(equity_index.values("equity__id"))
            )

        queryset = queryset.select_related("exchange")

        eod_data = EquityEndOfDay.backend.filter(
            date__gte=past_date, date__lt=date
        ).order_by("date")
        queryset = queryset.prefetch_related(
            Prefetch("eod_data", queryset=eod_data, to_attr="eod")
        )

        records = []
        for equity in queryset.all():
            eod_data = equity.eod

            js_array = []
            for eod in eod_data:
                js_array.append(eod.__dict__)

            if len(eod_data) == 0:
                continue

            df = pd.DataFrame(js_array)
            df = df.drop(["_state"], axis=1, errors="ignore")
            df.rename(
                columns={
                    "open_price": "open",
                    "high_price": "high",
                    "low_price": "low",
                    "close_price": "close",
                    "entity__symbol": "symbol",
                },
                inplace=True,
            )

            df["average_quantity_per_trade"] = (
                df["quantity_per_trade"].rolling(window=20).mean()
            )
            df["average_traded_quantity"] = (
                df["traded_quantity"].rolling(window=20).mean()
            )
            df["average_delivery_percentage"] = (
                df["delivery_percentage"].rolling(window=20).mean()
            )
            df["per_delivery_percentage"] = (
                df["delivery_percentage"].astype(float)
                / df["average_delivery_percentage"]
            )
            df["per_average_volumn"] = (
                df["traded_quantity"].astype(float) / df["average_traded_quantity"]
            )
            df["per_quantity_per_trade"] = (
                df["quantity_per_trade"].astype(float)
                / df["average_quantity_per_trade"]
            )
            df["MA_10"] = talib.EMA(df["close"], timeperiod=10)
            df = recognize_candlestick(df)

            js = df.iloc[-1].to_json()
            record = json.loads(js)
            record["symbol"] = equity.symbol
            record["date1"] = date
            records.append(record)

        records = sorted(records, key=itemgetter("candlestick_rank"), reverse=False)
        records = [d for d in records if d["candlestick_rank"] > 0]
        result = {
            "date": date,
            "count": len(records),
            "symbols": [sub["symbol"] for sub in records],
            "records": records,
        }
        return Response(result)

        # df = pd.DataFrame() # Empty DataFrame
        # df = df.ta.ticker("^NSEBANK", period="2d", interval="15m")
        # print(df)

        # df.rename(
        #             columns={
        #                 "Open": "open",
        #                 "High": "high",
        #                 "Low": "low",
        #                 "Close": "close",
        #             },
        #             inplace=True,
        #         )
        # with pd.option_context(
        #                     "display.max_rows",
        #                     None,
        #                     "display.max_columns",
        #                     None,
        #                     "display.width",
        #                     None,
        #                 ):
        #     df = recognize_candlestick(df)
        #     print(df)

        # equities = ["hdfcbank"]

        # df = pd.DataFrame(list(eod_data.values("date","prev_close",
        # "open_price", "high_price", "low_price", "last_price",
        # "close_price", "avg_price", "delivery_quantity",
        # "delivery_percentage", "percentage_changed",
        # "quantity_per_trade", "point_changed")))
        # df["point_changed2"] = df["close_price"].diff()
        # df["quantity_per_trade_avg"] = df["quantity_per_trade"].rolling(window=20).mean()

        # df1 = pd.DataFrame(
        #     list(
        #         eod_data.values(
        #             "date",
        #             "open_price",
        #             "high_price",
        #             "low_price",
        #             "close_price",
        #         )
        #     )
        # )
        # df1.rename(
        #     columns={
        #         "open_price": "open",
        #         "high_price": "high",
        #         "low_price": "low",
        #         "close_price": "close",
        #     },
        #     inplace=True,
        # )

        # df1["date"] = pd.to_datetime(
        #     df1["date"],
        #     format="%Y-%m-%d %H:%M:%S.%f %z",
        #     errors="coerce",
        #     utc=True,
        # )
        # df1["date"] = df1["date"].dt.tz_convert("Asia/Kolkata")
        # df1["MA5_mean"] = (
        #     talib.MA(df1["close"], timeperiod=5)
        #     / talib.MA(df1["close"], timeperiod=5).mean()
        # )
        # df1["MA5"] = talib.MA(df1["close"], timeperiod=5)

        # with pd.option_context(
        #     "display.max_rows",
        #     None,
        #     "display.max_columns",
        #     None,
        #     "display.width",
        #     None,
        # ):
        #     df1 = recognize_candlestick(df1)
        #     print(df1)

        #     # df2 = df1.ta.cdl_pattern("all")
        #     # print(df2)

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
