from operator import itemgetter

import pandas as pd
from django.db.models import Avg, Max, OuterRef, Prefetch, Subquery

import ontrack.ta as ta
from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.data.participant import PullParticipantData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.equity import EquityEndOfDay
from ontrack.market.models.lookup import Equity
from ontrack.ta.core import sanitize
from ontrack.users.models.lookup import StockScreener
from ontrack.utils.base.enum import HolidayCategoryType
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.config import Configurations as conf
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.numbers import NumberHelper as nh


class Screener(BaseLogic):
    def __init__(self, exchange_symbol: str, recorder=None):
        self.settings = SettingLogic()
        self.marketlookupdata = MarketLookupData(exchange_symbol)

        tp = TaskProgressStatus(recorder)
        self.tp = tp

        ex = self.marketlookupdata.exchange()
        eq = self.marketlookupdata.equity_dict()
        inx = self.marketlookupdata.index_dict()

        self.pull_equity_obj = PullEquityData(ex, eq, tp)
        self.pull_index_obj = PullIndexData(ex, inx, tp)
        self.pull_participant_obj = PullParticipantData(ex, tp)

    def get_queryset_stocks_by_index(self, index, only_fno=False):
        qs = None
        if only_fno:
            qs = Equity.backend.filter(lot_size__gt=0)
        else:
            qs = Equity.backend

        qs = qs.filter(equity_indices__index__symbol__iexact=index)
        qs = qs.prefetch_related("equity")
        qs = qs.prefetch_related("index")

        return qs

    def stock_screener_data(self, date=None, index=None, length=None, only_fno=False):
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if not length:
                length = conf.get_default_value_by_key("default_length_count")

            if not index:
                index = conf.get_default_value_by_key("default_index_symbol")

            date = dt.get_last_working_day(date)
            past_date = dt.get_past_date(date, days=length * 2)

            qs_equities = self.get_queryset_stocks_by_index(index, only_fno)
            sub_query_e_qs = Subquery(qs_equities.values("id"))

            columns = [
                "date",
                "entity__symbol",
                "prev_close",
                "open_price",
                "high_price",
                "low_price",
                "last_price",
                "close_price",
                "avg_price",
                "point_changed",
                "percentage_changed",
                "traded_quantity",
                "quantity_per_trade",
                "delivery_quantity",
                "delivery_percentage",
            ]

            e_eod_qs = EquityEndOfDay.backend
            e_eod_qs = e_eod_qs.filter(date__gte=past_date, date__lt=date).order_by(
                "date"
            )
            e_eod_qs = e_eod_qs.filter(entity_id__in=sub_query_e_qs)

            df = pd.DataFrame(list(e_eod_qs.values(*columns)))
            return sanitize(df)

    def stock_screener(
        self, screener_id, date=None, index=None, length=None, only_fno=False
    ):
        screener_qs = StockScreener.backend.filter(id=screener_id)
        screener_qs = screener_qs.prefetch_related("sections")
        screener = screener_qs.first()

        params = []
        for section in screener.sections.all():
            for itemObj in section.items.all():
                if itemObj.item:
                    params.append(itemObj.item.params)

        strategy = ta.Strategy(
            name="stock-selection",
            description="SMA and EMA 200, 100, 50, BBANDS, CPR",
            ta=[param["indicator"] for param in params],
        )

        df = self.stock_screener_data(date, index, length, only_fno)

        df_list = []
        dfg = df.groupby(["symbol"])
        for grp in dfg.groups:
            x = dfg.get_group(grp).copy()
            x.ta.strategy(strategy)
            df_list.append(x)
        newdf = pd.concat(df_list)

        return newdf

    def stock_screener_hidden_move(self, date, index=None, length=None):
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if not length:
                length = conf.get_default_value_by_key("default_length_count")

            if not index:
                index = conf.get_default_value_by_key("default_index_symbol")

            date = dt.get_last_working_day(date)
            past_date = dt.get_past_date(date, days=length + 1)

            e_eod_qs = EquityEndOfDay.backend.values("entity_id")
            e_eod_qs = e_eod_qs.filter(date__gte=past_date, date__lt=date)
            e_eod_qs = e_eod_qs.annotate(avg_qpt=Avg("quantity_per_trade") * 2)
            e_eod_qs = e_eod_qs.filter(entity_id=OuterRef("entity_id"))

            sub_query_eod_qs = Subquery(e_eod_qs.values("avg_qpt")[:1])

            eod_latest_qs = EquityEndOfDay.backend.filter(date=date)
            eod_latest_qs = eod_latest_qs.filter(
                quantity_per_trade__gt=sub_query_eod_qs
            )

            sub_query_e_qs = Subquery(eod_latest_qs.values("entity_id"))
            qs = Equity.backend.filter(id__in=sub_query_e_qs)

            qs = qs.filter(equity_indices__index__symbol__iexact=index)
            qs = qs.annotate(weightage=Max("equity_indices__equity_weightage"))

            eod_qs = EquityEndOfDay.backend
            eod_qs = eod_qs.filter(date__gte=past_date, date__lte=date).order_by("date")
            qs = qs.prefetch_related(
                Prefetch("eod_data", queryset=eod_qs, to_attr="eod")
            )

            records = []
            for equity in qs.all():
                eod_data = equity.eod

                js_array = []
                for eod in eod_data:
                    js_array.append(eod.__dict__)

                if len(eod_data) == 0:
                    continue

                df = pd.DataFrame(js_array)
                df = df.drop(["_state"], axis=1, errors="ignore")
                result = self.populate_indicators(df)

                df = result[0]
                row = df.ta.last_record

                record = {}
                record["id"] = equity.id
                record["symbol"] = equity.symbol
                record["weightage"] = nh.roundOff(equity.weightage)
                record["slug"] = equity.slug
                record["candlestick"] = row[1]
                records.append(record)

            records = sorted(records, key=itemgetter("weightage"), reverse=True)
            result = {
                "date": date,
                "count": len(records),
                "records": records,
            }
            return result

    def populate_indicators(self, df):
        strategy = ta.Strategy(
            name="stock-selection",
            description="SMA and EMA 200, 100, 50, BBANDS, CPR",
            ta=[
                {"kind": "sma", "length": 200},
                {"kind": "sma", "length": 100},
                {"kind": "sma", "length": 50},
                {"kind": "ema", "length": 200},
                {"kind": "ema", "length": 100},
                {"kind": "ema", "length": 50},
                {"kind": "ema", "length": 5},
                {"kind": "ema", "length": 9},
                {"kind": "ema", "length": 13},
                {"kind": "bbands", "length": 20, "std": 1.5},
                {"kind": "cpr"},
                {"kind": "sma", "close": "CPR", "length": 20, "prefix": "CPR"},
                {"kind": "amat"},
                {
                    "kind": "cdl_pattern",
                    "name": "all",
                    "consolidated": True,
                    "append": True,
                },
                # {
                #     "kind": "ratio",
                #     "close": "quantity_per_trade",
                #     "length": 20,
                #     "prefix": "QPT",
                # },
                # {"kind": "ratio", "close": "volume", "length": 20, "prefix": "VOL"},
                # {
                #     "kind": "ratio",
                #     "close": "delivery_percentage",
                #     "length": 20,
                #     "prefix": "DEL_P",
                # },
                # {
                #     "kind": "ratio",
                #     "close": "delivery_quantity",
                #     "length": 20,
                #     "prefix": "DEL_QTY",
                # },
            ],
        )
        df.ta.cores = 0
        df.ta.sanitize()
        df.ta.strategy(strategy)

        row = df.ta.last_record

        cdl_rows = []
        cdl_string = row["CDL_CONSOLIDATED"].strip()
        if cdl_string:
            for cdl in cdl_string.split(";"):
                cdl_rs = cdl.split("|")
                name = cdl_rs[0]
                score = nh.str_to_float(cdl_rs[1])

                cdl_row = {}
                cdl_row["rank"] = 0
                cdl_row["name"] = name
                cdl_row["sentiment"] = "BULLISH" if score > 0 else "BEARISH"
                cdl_row["score"] = score
                cdl_rows.append(cdl_row)

        cdl_rows = sorted(cdl_rows, key=itemgetter("rank"), reverse=False)

        return df.ta.dataframe, cdl_rows
