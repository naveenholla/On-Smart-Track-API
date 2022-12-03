from operator import itemgetter

import pandas as pd
from django.db import transaction
from django.db.models import Avg, Max, OuterRef, Prefetch, Subquery

import ontrack.ta as ta
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

    def load_equity_corporate_action(self, date):
        result = self.pull_equity_obj.pull_parse_corporate_action(date)
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

    def __save_equity_eod(self, result, modeltype, title):
        records_stats = self.create_or_update(result, modeltype)
        stats = self.message_creator(f"{title}", records_stats)
        self.tp.log_records_stats(stats, f"{title} - Stats")
        return stats

    def __update_company_action(self, results):
        if results is None:
            return

        for action in results:
            subject = action["subject"]
            symbol = action["symbol"]
            exDate = action["exDate"]
            entry_type = action["entry_type"]
            values = action["values"]

            multiplier = 0
            if entry_type == "bonus":
                multiplier = values[0] + values[1]
            elif entry_type == "split":
                multiplier = values[0] / values[1]
            else:
                continue

            self.tp.log_message(f"{symbol} - {exDate} - {entry_type} - {subject}")
            self.tp.log_message(f"Multiplier: {multiplier}")

            updated_records = []
            records = EquityEndOfDay.backend.filter(
                entity__symbol__iexact=symbol, date__lt=exDate
            )
            record_exdate = EquityEndOfDay.backend.filter(
                entity__symbol__iexact=symbol, date=exDate
            ).first()

            if record_exdate:
                close = float(record_exdate.close_price)
                preclose = float(record_exdate.prev_close) / multiplier
                pointchanged = close - preclose
                record_exdate.prev_close = nh.round_to_market_Price(preclose)
                record_exdate.point_changed = nh.round_to_market_Price(pointchanged)
                record_exdate.percentage_changed = nh.round_to_market_Price(
                    pointchanged / close * 100
                )
                updated_records.append(record_exdate)

            for record in records:
                price = float(record.prev_close)
                converted = nh.round_to_market_Price(price / multiplier)
                record.prev_close = converted

                price = float(record.open_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.open_price = converted

                price = float(record.high_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.high_price = converted

                price = float(record.low_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.low_price = converted

                price = float(record.last_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.last_price = converted

                price = float(record.close_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.close_price = converted

                price = float(record.avg_price)
                converted = nh.round_to_market_Price(price / multiplier)
                record.avg_price = converted

                price = float(record.point_changed)
                converted = nh.round_to_market_Price(price / multiplier)
                record.point_changed = converted

                price = float(record.traded_quantity)
                converted = nh.round_to_market_Price(price * multiplier)
                record.traded_quantity = converted

                price = float(record.delivery_quantity)
                converted = nh.round_to_market_Price(price * multiplier)
                record.delivery_quantity = converted

                price = record.traded_quantity / float(record.number_of_trades)
                record.quantity_per_trade = price

                updated_records.append(record)

            EquityEndOfDay.backend.bulk_update(
                updated_records,
                [
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
                ],
            )

            self.tp.log_message(f"Updated: {len(updated_records)}")

    def execute_equity_eod_data_task(self, run_date=None, end_date=None):
        self.output = []
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            if self.marketlookupdata.exchange() is None:
                self.tp.log_warning("Exchange is required.")
                return "Exchange is required."

            date_key = sk.DATAPULL_EQUITY_EOD_LAST_PULL_DATE
            pause_hour_key = sk.DATAPULL_EOD_DATA_PAUSE_HOURS
            default_start_key = sk.DEFAULT_START_DATE_EQUITY_DATA_PULL

            if not run_date:
                cet = self.can_execute_task(date_key, pause_hour_key, default_start_key)
                if not cet[0]:
                    message = cet[1]
                    self.tp.log_message(message)
                    self.output.append(self.message_creator("EOD", message))
                    return self.output
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
                    self.output.append(self.message_creator(run_date_str, message))
                    self.tp.log_message(message)
                    continue

                if not dt.is_data_refreshed(run_date, end_date):
                    run_date = dt.get_future_date(run_date, hours=pause_hours)
                    message = "Data is not refreshed yet."
                    self.output.append(self.message_creator(run_date_str, message))
                    self.tp.log_message(message)
                    continue

                try:
                    re = self.load_equity_eod_data(run_date)
                    reca = self.load_equity_corporate_action(run_date)
                    red = self.load_equity_derivative_eod_data(run_date)

                    if isinstance(re, str):
                        self.output.append(self.message_creator(run_date_str, re))
                    else:
                        with transaction.atomic():
                            e_stats = self.__save_equity_eod(
                                re, EquityEndOfDay, "Equities"
                            )
                            self.__update_company_action(reca)
                            d_stats = self.__save_equity_eod(
                                red, EquityDerivativeEndOfDay, "Derivatives"
                            )

                            stats = self.message_creator(
                                run_date_str, [e_stats, d_stats]
                            )
                            self.output.append(stats)
                            if not end_date_provided:
                                self.settings.save_task_execution_time(
                                    date_key, run_date
                                )

                except Exception as e:
                    message = f"Exception - `{format(e)}`."
                    self.tp.log_error(message=message)
                    self.output.append(self.message_creator(run_date_str, message))
                    raise

                run_date = dt.get_future_date(run_date, hours=pause_hours)

            self.tp.log_completed("Task Completed.")
            return self.output

    def get_all_fno_stocks(self, index=None):
        qs = Equity.backend.filter(lot_size__gt=0)

        if index:
            qs = qs.filter(equity_indices__index__symbol__iexact=index)

        qs = qs.prefetch_related("equity")
        qs = qs.prefetch_related("index")

        return qs

    def stock_selection_hidden_move(self, date, index=None, avg_days=None):
        with application_context(
            exchange=self.marketlookupdata.exchange(),
            holiday_category_name=HolidayCategoryType.EQUITIES,
        ):
            date = dt.get_last_working_day(date)

            if not avg_days:
                avg_days = conf.get_default_value_by_key("default_average_count")

            if not index:
                index = "cnx750"

            past_date = dt.get_past_date(date, days=avg_days + 1)

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
