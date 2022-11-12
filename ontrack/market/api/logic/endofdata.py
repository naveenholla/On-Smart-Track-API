from operator import itemgetter

import pandas as pd
import talib
from django.db import transaction
from django.db.models import Avg, Max, OuterRef, Prefetch, Subquery

from ontrack.lookup.api.logic.settings import SettingLogic
from ontrack.market.api.data.equity import PullEquityData
from ontrack.market.api.data.index import PullIndexData
from ontrack.market.api.data.participant import PullParticipantData
from ontrack.market.api.logic.lookup import MarketLookupData
from ontrack.market.models.equity import EquityDerivativeEndOfDay, EquityEndOfDay
from ontrack.market.models.index import IndexDerivativeEndOfDay, IndexEndOfDay
from ontrack.market.models.lookup import Equity
from ontrack.market.models.participant import (
    ParticipantActivity,
    ParticipantStatsActivity,
)
from ontrack.ta.candles.cdl_recognization import recognize_candlestick
from ontrack.utils.base.enum import AdminSettingKey as sk
from ontrack.utils.base.enum import HolidayCategoryType
from ontrack.utils.base.logic import BaseLogic
from ontrack.utils.base.tasks import TaskProgressStatus
from ontrack.utils.config import Configurations as conf
from ontrack.utils.context import application_context
from ontrack.utils.datetime import DateTimeHelper as dt
from ontrack.utils.numbers import NumberHelper as nh


class EndOfDayData(BaseLogic):
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

    def load_equity_eod_data(self, date):
        already_processed = EquityEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_equity_obj.pull_parse_eod_data(date)

        return result

    def load_equity_derivative_eod_data(self, date):
        already_processed = EquityDerivativeEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_equity_obj.pull_parse_derivative_eod_data(date)

        return result

    def load_index_eod_data(self, date):
        already_processed = IndexEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_index_obj.pull_parse_eod_data(date)

        return result

    def load_index_derivative_eod_data(self, date):
        already_processed = IndexDerivativeEndOfDay.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_index_obj.pull_parse_derivative_eod_data(date)

        return result

    def load_participant_eod_data(self, date):
        already_processed = ParticipantActivity.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_participant_obj.pull_parse_eod_data(date)

        return result

    def load_participant_stats_eod_data(self, date, save_data=True):
        already_processed = ParticipantStatsActivity.backend.filter(date=date).count()
        if already_processed > 0:
            return "Already Processed."

        result = self.pull_participant_obj.pull_parse_eod_stats(date)

        return result

    def execute_equity_eod_data_task(self, run_date=None, end_date=None):
        output = []
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if self.marketlookupdata.exchange() is None:
                self.tp.log_warning("Exchange is required.")
                return "Exchange is required."

            date_key = sk.DATAPULL_EQUITY_EOD_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS

            if not run_date:
                cet = self.can_execute_task(date_key, pause_hour_key)
                if not cet[0]:
                    message = cet[1]
                    self.tp.log_message(message)
                    return message
                run_date = cet[2]

            end_date_provided = True
            if not end_date:
                end_date_provided = False
                end_date = dt.current_date_time()

            pause_hours = self.settings.get_by_key(pause_hour_key)
            pause_hours = nh.str_to_float(pause_hours)

            self.tp.log_debug(f"End Date:{end_date}")
            self.tp.log_debug(f"Date:{run_date}")

            while dt.compare_date_time(run_date, end_date, "lte"):
                self.tp.log_debug(f"Processing Date:{run_date}")
                run_date_str = dt.datetime_to_display_str(run_date)

                if dt.is_holiday(run_date):
                    self.settings.save_task_execution_time(date_key, run_date)
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "It a is holiday."
                    output.append(self.message_creator(run_date_str, message))
                    self.tp.log_message(message)
                    continue

                if not dt.is_data_refreshed(run_date, end_date):
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "Data is not refreshed yet."
                    output.append(self.message_creator(run_date_str, message))
                    self.tp.log_message(message)
                    continue

                try:
                    result = self.load_equity_eod_data(run_date)
                    if isinstance(result, str):
                        output.append(self.message_creator(run_date_str, result))
                    else:
                        with transaction.atomic():
                            records_stats = self.create_or_update(
                                result, EquityEndOfDay
                            )
                            if not end_date_provided:
                                self.settings.save_task_execution_time(
                                    date_key, run_date
                                )
                        stats = self.message_creator(run_date_str, records_stats)
                        output.append(stats)
                        self.tp.log_records_stats(stats)
                except Exception as e:
                    message = f"Exception - `{format(e)}`."
                    self.tp.log_error(message=message)
                    output.append(self.message_creator(run_date_str, message))
                    raise

                run_date = dt.get_future_date(run_date, hours=pause_hours)

                self.tp.log_completed("Task Completed.")
            return output

    def stock_selection_hidden_move(self, date, index, avg_days):
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            date = dt.get_last_working_day(date)

            if not avg_days:
                avg_days = conf.get_default_value_by_key("default_average_count")

            if not index:
                index = "cnx750"

            past_date = dt.get_past_date(date, days=avg_days)

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

                key = "quantity_per_trade"
                window = 20
                df["qpt_avg"] = df[key].rolling(window=window).mean()
                df["qpt_ratio"] = df[key].astype(float) / df["qpt_avg"]

                key = "traded_quantity"
                df["vol_avg"] = df[key].rolling(window=window).mean()
                df["vol_ratio"] = df[key].astype(float) / df["vol_avg"]

                key = "delivery_percentage"
                df["del_avg"] = df[key].rolling(window=window).mean()
                df["del_ratio"] = df[key].astype(float) / df["del_avg"]

                df["MA_10"] = talib.EMA(df["close"], timeperiod=10)
                df = recognize_candlestick(df)

                df = df.fillna(0)
                row = df.iloc[-1]
                record = {}
                record["id"] = equity.id
                record["symbol"] = equity.symbol
                record["weightage"] = nh.roundOff(equity.weightage)
                record["slug"] = equity.slug
                record["qpt_ratio"] = nh.roundOff(row["qpt_ratio"])
                record["vol_ratio"] = nh.roundOff(row["vol_ratio"])
                record["del_ratio"] = nh.roundOff(row["del_ratio"])

                cdl_rows = []
                for cdl in row["candlestick"].split(";"):
                    cdl_rs = cdl.split("|")
                    cdl_row = {}
                    cdl_row["rank"] = nh.str_to_float(cdl_rs[0])
                    cdl_row["name"] = cdl_rs[1]
                    cdl_row["sentiment"] = cdl_rs[2]
                    cdl_row["score"] = nh.str_to_float(cdl_rs[3])
                    cdl_rows.append(cdl_row)

                cdl_rows = sorted(cdl_rows, key=itemgetter("rank"), reverse=False)
                record["candlestick"] = cdl_rows
                record["candlestick_pattern"] = row["candlestick_pattern"]
                record["candlestick_rank"] = row["candlestick_rank"]
                records.append(record)

            records = sorted(records, key=itemgetter("weightage"), reverse=True)
            records = [d for d in records if d["candlestick_rank"] > 0]
            result = {
                "date": date,
                "count": len(records),
                "records": records,
            }
            return result
